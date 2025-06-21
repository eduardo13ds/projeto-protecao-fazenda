# app/mqtt/client.py
import json
import ssl
from datetime import datetime
from app.extensions import db
from paho.mqtt import client as mqtt
from app.models.registro_leitura import RegistroLeitura
from app.models.dispositivo import Dispositivo
from app.models.sensor import Sensor
from app.models.tipo_sensor import TipoSensor

# Variáveis globais para dados em tempo real (mantidas para compatibilidade)
latest_data_by_area = {}
latest_data = {}
latest_inmet_data = {}

# O novo mapa de sensores. Estrutura:
# { 'id_unico_dispositivo': { 'nome_tipo_sensor': id_sensor_no_db, ... }, ... }
# Exemplo: { 'sensor_area_norte_01': { 'temperatura': 1, 'umidade': 2 } }
SENSOR_MAP = {}
DEVICE_MAP = {}  # Mapa adicional para informações dos dispositivos


class MQTTClient:
    def __init__(self, app=None):
        self.client = None
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        with self.app.app_context():
            self._load_sensor_map()

        self.client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(
            app.config["MQTT_USERNAME"], app.config["MQTT_PASSWORD"]
        )

        try:
            self.client.connect(app.config["MQTT_BROKER"], app.config["MQTT_PORT"])
            self.client.loop_start()
            self.app.logger.info("Cliente MQTT conectado com sucesso!")
        except Exception as e:
            self.app.logger.error(f"Falha ao conectar ao broker MQTT: {e}")

    def _load_sensor_map(self):
        """
        Carrega um mapa aninhado de todos os sensores do sistema.
        Mapeia [identificador_unico_dispositivo] -> [nome_tipo_sensor] -> [id_sensor].
        Também carrega informações dos dispositivos para referência rápida.
        """
        global SENSOR_MAP, DEVICE_MAP
        try:
            # Query otimizada que junta as tabelas necessárias
            results = (
                db.session.query(
                    Dispositivo.identificador_unico,
                    Dispositivo.id_dispositivo,
                    Dispositivo.nome_amigavel,
                    Dispositivo.area,
                    Dispositivo.status,
                    TipoSensor.nome_tipo,
                    TipoSensor.unidade_medida,
                    Sensor.id_sensor,
                    Sensor.status.label("sensor_status"),
                )
                .select_from(Dispositivo)
                .join(Sensor, Dispositivo.id_dispositivo == Sensor.id_dispositivo)
                .join(TipoSensor, Sensor.id_tipo_sensor == TipoSensor.id_tipo_sensor)
                .filter(Dispositivo.status == "Ativo")
                .filter(Sensor.status == "Ativo")
                .all()
            )

            new_sensor_map = {}
            new_device_map = {}

            for row in results:
                device_id = row.identificador_unico

                # Mapear informações do dispositivo
                if device_id not in new_device_map:
                    new_device_map[device_id] = {
                        "id_dispositivo": row.id_dispositivo,
                        "nome_amigavel": row.nome_amigavel,
                        "area": row.area,
                        "status": row.status,
                        "sensores": {},
                    }

                # Mapear sensores do dispositivo
                if device_id not in new_sensor_map:
                    new_sensor_map[device_id] = {}

                # Armazena tanto o nome exato quanto uma versão em minúsculas para flexibilidade
                sensor_type_key = row.nome_tipo.lower().strip()
                new_sensor_map[device_id][sensor_type_key] = {
                    "id_sensor": row.id_sensor,
                    "nome_tipo": row.nome_tipo,
                    "unidade_medida": row.unidade_medida,
                    "status": row.sensor_status,
                }

                # Adiciona também ao mapa de dispositivos para referência
                new_device_map[device_id]["sensores"][sensor_type_key] = {
                    "id_sensor": row.id_sensor,
                    "nome_tipo": row.nome_tipo,
                    "unidade_medida": row.unidade_medida,
                }

            SENSOR_MAP = new_sensor_map
            DEVICE_MAP = new_device_map

            self.app.logger.info(
                f"Mapa de sensores carregado: {len(new_device_map)} dispositivos, "
                f"{sum(len(sensors) for sensors in new_sensor_map.values())} sensores ativos"
            )

            # Log detalhado dos dispositivos carregados
            for device_id, device_info in new_device_map.items():
                sensor_types = list(device_info["sensores"].keys())
                self.app.logger.debug(
                    f"Dispositivo '{device_id}': {len(sensor_types)} sensores ({', '.join(sensor_types)})"
                )

        except Exception as e:
            self.app.logger.error(
                f"Falha crítica ao carregar o mapa de sensores do banco: {e}"
            )
            SENSOR_MAP = {}
            DEVICE_MAP = {}

    def _on_connect(self, client, userdata, flags, reasonCode, properties=None):
        if reasonCode == 0:
            self.app.logger.info("Conectado ao Broker MQTT com sucesso!")
            client.subscribe("sensor/dados", qos=0)
            client.subscribe("inmet/dados", qos=0)
        else:
            self.app.logger.error(
                f"Falha ao conectar ao MQTT Broker, código de retorno: {reasonCode}"
            )

    def _on_message(self, client, userdata, msg):
        global latest_data, latest_data_by_area, latest_inmet_data
        try:
            data = json.loads(msg.payload.decode())
            self.app.logger.debug(f"Mensagem recebida do tópico '{msg.topic}': {data}")

            if msg.topic == "sensor/dados":
                with self.app.app_context():
                    success = self._save_data_to_db(data)
                    if success:
                        self._update_device_ping(data.get("device_id"))

                # Mantém lógica de tempo real para compatibilidade
                if "area" in data:
                    latest_data_by_area[data["area"]] = data
                latest_data = data

            elif msg.topic == "inmet/dados":
                latest_inmet_data = data

        except json.JSONDecodeError as e:
            self.app.logger.error(f"Erro ao decodificar JSON da mensagem MQTT: {e}")
        except Exception as e:
            self.app.logger.error(f"Erro ao processar mensagem MQTT: {e}")

    def _save_data_to_db(self, data):
        """
        Salva as leituras no banco de dados, usando o device_id para identificar a origem.
        Retorna True se pelo menos uma leitura foi salva com sucesso.
        """
        device_id = data.pop("device_id", None)
        if not device_id:
            self.app.logger.warning(
                f"Mensagem recebida sem 'device_id'. Ignorando: {data}"
            )
            return False

        # Verifica se o dispositivo é conhecido pelo sistema
        device_sensors_map = SENSOR_MAP.get(device_id)
        device_info = DEVICE_MAP.get(device_id)

        if not device_sensors_map or not device_info:
            self.app.logger.warning(
                f"Dispositivo '{device_id}' desconhecido ou inativo. "
                f"Mensagem ignorada. Verifique o cadastro e status."
            )
            # Recarrega o mapa caso um novo dispositivo tenha sido cadastrado
            self._load_sensor_map()
            return False

        now = datetime.utcnow()
        registros_para_adicionar = []
        registros_processados = 0

        for key, value in data.items():
            if key in ["area", "timestamp"]:  # Ignora campos de controle
                continue

            # Busca o sensor no mapa, tentando diferentes variações da chave
            sensor_info = None
            search_keys = [
                key.lower().strip(),
                key.replace("_", " ").lower().strip(),
                key.replace(" ", "_").lower().strip(),
            ]

            for search_key in search_keys:
                if search_key in device_sensors_map:
                    sensor_info = device_sensors_map[search_key]
                    break

            if not sensor_info:
                self.app.logger.debug(
                    f"Tipo de sensor '{key}' não encontrado no dispositivo '{device_id}'. "
                    f"Sensores disponíveis: {list(device_sensors_map.keys())}"
                )
                continue

            if value is None or value == "":
                self.app.logger.debug(
                    f"Valor vazio/nulo para '{key}' do dispositivo '{device_id}'"
                )
                continue

            try:
                # Tenta converter valor para numérico
                valor_str = str(value).replace(",", ".")
                valor_float = float(valor_str)

                # Cria o registro de leitura
                novo_registro = RegistroLeitura(
                    id_sensor=sensor_info["id_sensor"],
                    valor_leitura=valor_str,
                    timestamp_leitura=now,
                    valor_numerico=valor_float,
                    unidade_medida=sensor_info["unidade_medida"],
                )

                # Valida a qualidade da leitura
                novo_registro.validar_qualidade()

                registros_para_adicionar.append(novo_registro)
                registros_processados += 1

            except (ValueError, TypeError) as e:
                self.app.logger.warning(
                    f"Valor '{value}' para '{key}' do dispositivo '{device_id}' "
                    f"não é um número válido: {e}"
                )

        # Salva todos os registros válidos
        if registros_para_adicionar:
            try:
                db.session.add_all(registros_para_adicionar)
                db.session.commit()
                self.app.logger.info(
                    f"{len(registros_para_adicionar)} registros do dispositivo "
                    f"'{device_id}' ({device_info['nome_amigavel']}) salvos no DB."
                )
                return True

            except Exception as e:
                db.session.rollback()
                self.app.logger.error(
                    f"Falha ao salvar registros do dispositivo '{device_id}' no DB: {e}"
                )
                return False
        else:
            if registros_processados == 0:
                self.app.logger.warning(
                    f"Nenhum sensor válido encontrado na mensagem do dispositivo '{device_id}'"
                )
            return False

    def _update_device_ping(self, device_id):
        """Atualiza o timestamp do último ping do dispositivo"""
        if not device_id:
            return

        try:
            dispositivo = Dispositivo.query.filter_by(
                identificador_unico=device_id
            ).first()
            if dispositivo:
                dispositivo.ultimo_ping = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            self.app.logger.error(
                f"Erro ao atualizar ping do dispositivo '{device_id}': {e}"
            )
            db.session.rollback()

    def reload_sensor_map(self):
        """Método público para recarregar o mapa de sensores"""
        with self.app.app_context():
            self._load_sensor_map()

    def get_device_info(self, device_id):
        """Obtém informações de um dispositivo específico"""
        return DEVICE_MAP.get(device_id)

    def get_all_devices(self):
        """Retorna informações de todos os dispositivos"""
        return DEVICE_MAP.copy()

    def get_device_sensors(self, device_id):
        """Obtém os sensores de um dispositivo específico"""
        return SENSOR_MAP.get(device_id, {})

    # Funções de get em tempo real (mantidas para compatibilidade)
    def get_all_latest_data(self):
        return latest_data_by_area.copy()

    def get_latest_data(self, area_id=None):
        if area_id:
            return latest_data_by_area.get(int(area_id), {})
        return latest_data

    def get_latest_inmet_data(self):
        return latest_inmet_data


# Instância global do cliente MQTT
mqtt_client = MQTTClient()
