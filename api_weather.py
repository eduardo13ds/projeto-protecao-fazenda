import requests
import json # Importado para referência, mas response.json() é o principal
import paho.mqtt.client as mqtt
import time

# URL da API Open-Meteo para Paranaguá (-25.52, -48.51)
# Busca dados 'current' (última hora) e 'daily' (agregados para hoje)
api_url = "https://api.open-meteo.com/v1/forecast?latitude=-25.65778&longitude=-49.30778&current=relative_humidity_2m,dew_point_2m,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m&daily=dew_point_2m_max,dew_point_2m_min,surface_pressure_max,surface_pressure_min,shortwave_radiation_sum&temperature_unit=celsius&wind_speed_unit=ms&pressure_unit=hpa&timezone=UTC&forecast_days=1"

# Variáveis para armazenar os dados
data_str = "N/D"
hora_utc_str = "N/D"
umidade_relativa = "N/D"
pto_orvalho_ins = "N/D"
pto_orvalho_max = "N/D"
pto_orvalho_min = "N/D"
pressao_ins = "N/D"
pressao_max = "N/D"
pressao_min = "N/D"
vel_vento = "N/D"
dir_vento = "N/D"
raj_vento = "N/D"
radiacao_kj_m2 = "N/D"

api_response_data = None # Para guardar a resposta completa em caso de erro de parsing

print(f"Buscando dados meteorológicos para Paranaguá (-25.52, -48.51)...")

try:
    # 1. Fazer a requisição HTTP GET
    response = requests.get(api_url)
    response.raise_for_status()  # Levanta um erro HTTP para status ruins (4xx ou 5xx)

    # 2. Parsear a resposta JSON
    weather_data = response.json()
    api_response_data = weather_data # Guardar para debug se necessário

    # 3. Extrair os dados 'current' (última hora disponível)
    current_weather = weather_data.get("current")
    if current_weather:
        current_time_str = current_weather.get("time")
        if current_time_str:
            parts = current_time_str.split("T")
            if len(parts) == 2:
                data_str = parts[0]
                hora_utc_str = parts[1]
        
        umidade_relativa = current_weather.get("relative_humidity_2m")
        pto_orvalho_ins = current_weather.get("dew_point_2m")
        pressao_ins = current_weather.get("surface_pressure")
        vel_vento = current_weather.get("wind_speed_10m")
        dir_vento = current_weather.get("wind_direction_10m")
        raj_vento = current_weather.get("wind_gusts_10m")

    # 4. Extrair os dados 'daily' (para o dia corrente - primeiro item das listas)
    daily_weather = weather_data.get("daily")
    if daily_weather:
        # Função auxiliar para pegar o primeiro item de uma lista se existir
        def get_first_daily_value(key):
            data_list = daily_weather.get(key)
            if data_list and isinstance(data_list, list) and len(data_list) > 0:
                return data_list[0]
            return "N/D"

        pto_orvalho_max = get_first_daily_value("dew_point_2m_max")
        pto_orvalho_min = get_first_daily_value("dew_point_2m_min")
        pressao_max = get_first_daily_value("surface_pressure_max")
        pressao_min = get_first_daily_value("surface_pressure_min")
        
        radiacao_sum_j_m2 = get_first_daily_value("shortwave_radiation_sum")
        if radiacao_sum_j_m2 != "N/D" and radiacao_sum_j_m2 is not None:
            radiacao_kj_m2 = float(radiacao_sum_j_m2) / 1000.0
        else:
            radiacao_kj_m2 = "N/D"

    # 5. Mostrar os dados em formato de tabela
    print("\n" + "="*50)
    print("Dados Meteorológicos da Última Hora e Diário de Hoje")
    print("="*50)
    print(f"{'Parâmetro':<28} | {'Valor'}")
    print("-"*50)
    
    # Função para formatar valor, tratando None e "N/D"
    def format_value(value, unit="", precision=None):
        if value is None or value == "N/D":
            return "N/D"
        if precision is not None:
            try:
                return f"{float(value):.{precision}f} {unit}".strip()
            except ValueError:
                return f"{value} {unit}".strip() # Caso não seja numérico após tudo
        return f"{value} {unit}".strip()

    print(f"{'Data':<28} | {format_value(data_str)}")
    print(f"{'Hora (UTC)':<28} | {format_value(hora_utc_str)}")
    print(f"{'Umidade Relativa':<28} | {format_value(umidade_relativa, '%')}")
    print(f"{'Pto Orvalho Ins.':<28} | {format_value(pto_orvalho_ins, '°C')}")
    print(f"{'Pto Orvalho Max. (Hoje)':<28} | {format_value(pto_orvalho_max, '°C')}")
    print(f"{'Pto Orvalho Min. (Hoje)':<28} | {format_value(pto_orvalho_min, '°C')}")
    print(f"{'Pressão Ins.':<28} | {format_value(pressao_ins, 'hPa')}")
    print(f"{'Pressão Max. (Hoje)':<28} | {format_value(pressao_max, 'hPa')}")
    print(f"{'Pressão Min. (Hoje)':<28} | {format_value(pressao_min, 'hPa')}")
    print(f"{'Vel. Vento':<28} | {format_value(vel_vento, 'm/s')}")
    print(f"{'Dir. Vento':<28} | {format_value(dir_vento, '°')}")
    print(f"{'Raj. Vento':<28} | {format_value(raj_vento, 'm/s')}")
    print(f"{'Radiação (Hoje)':<28} | {format_value(radiacao_kj_m2, 'KJ/m²', precision=2 if isinstance(radiacao_kj_m2, float) else None)}")
    print("-"*50)

    # Mostrar unidades (opcional, para referência)
    if api_response_data:
        print("\nUnidades conforme a API (para referência):")
        current_units = api_response_data.get("current_units", {})
        daily_units = api_response_data.get("daily_units", {})
        print(f"  Umidade: {current_units.get('relative_humidity_2m', 'N/A')}")
        print(f"  Ponto de Orvalho: {current_units.get('dew_point_2m', 'N/A')}")
        print(f"  Pressão: {current_units.get('surface_pressure', 'N/A')}")
        print(f"  Vel. Vento: {current_units.get('wind_speed_10m', 'N/A')}")
        print(f"  Radiação (soma diária): {daily_units.get('shortwave_radiation_sum', 'J/m²')} (convertido para KJ/m² no script)")

    # Montar dicionário no formato solicitado
    def format_json_value(value, casas=1):
        if value is None or value == "N/D":
            return "N/D"
        try:
            # Se for float, formata com vírgula
            if isinstance(value, float):
                return f"{value:.{casas}f}".replace(".", ",")
            # Se for int, retorna como string
            if isinstance(value, int):
                return str(value)
            # Se for string numérica, tenta converter
            v = float(value)
            return f"{v:.{casas}f}".replace(".", ",")
        except Exception:
            return str(value)

    dados_json = {
        "Data": data_str if data_str != "N/D" else "",
        "Hora (UTC)": int(hora_utc_str.replace(":", "")) if hora_utc_str != "N/D" and ":" in hora_utc_str else hora_utc_str,
        "Pto Orvalho Ins. (C)": format_json_value(pto_orvalho_ins),
        "Pto Orvalho Max. (C)": format_json_value(pto_orvalho_max),
        "Pto Orvalho Min. (C)": format_json_value(pto_orvalho_min),
        "Pressao Ins. (hPa)": format_json_value(pressao_ins, 1),
        "Pressao Max. (hPa)": format_json_value(pressao_max, 1),
        "Pressao Min. (hPa)": format_json_value(pressao_min, 1),
        "Vel. Vento (m/s)": format_json_value(vel_vento, 1),
        "Dir. Vento (m/s)": format_json_value(dir_vento, 1),
        "Raj. Vento (m/s)": format_json_value(raj_vento, 1),
        "Radiacao (KJ/m²)": format_json_value(radiacao_kj_m2, 2),
        "Chuva (mm)": "0,0"
    }

    # Exemplo de exibição do JSON
    print("\nJSON dos dados no formato solicitado:")
    dados_to_send = json.dumps(dados_json, ensure_ascii=False, indent=2)


except requests.exceptions.RequestException as e:
    print(f"\nErro ao fazer a requisição à API: {e}")
except (KeyError, IndexError, TypeError, AttributeError) as e:
    print(f"\nErro ao processar os dados recebidos da API: {e}")
    if api_response_data:
        print("\nDados recebidos da API (para depuração):")
        print(json.dumps(api_response_data, indent=2))
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")

# --- Configuração do MQTT HiveMQ Cloud ---
HIVEMQ_HOST = "fd2522b769fc4f16bb479a6cac3dcb7b.s1.eu.hivemq.cloud"
HIVEMQ_PORT = 8883
HIVEMQ_USER = "hivemq.webclient.1743567366904"
HIVEMQ_PASS = "02DGadKA1Bb3fcCg.,;&"
MQTT_TOPIC = "inmet/dados"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Conectado ao HiveMQ com sucesso!")
    else:
        print(f"Falha na conexão. Código de retorno: {rc}")

def on_publish(client, userdata, mid):
    print(f"Mensagem publicada com ID: {mid}")

import ssl
client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
client.on_connect = on_connect
client.on_publish = on_publish
client.tls_set(tls_version=ssl.PROTOCOL_TLS)
client.username_pw_set(HIVEMQ_USER, HIVEMQ_PASS)
client.connect(HIVEMQ_HOST, HIVEMQ_PORT)
client.loop_start()

result = client.publish(MQTT_TOPIC, dados_to_send, qos=1)
result.wait_for_publish()
if result.rc == mqtt.MQTT_ERR_SUCCESS:
    print(f"Enviado ao HiveMQ: {dados_to_send}")
else:
    print(f"Falha ao enviar mensagem: {mqtt.error_string(result.rc)}")
time.sleep(0.1)

client.loop_stop()
client.disconnect()
print("\nProcessamento e envio concluídos.")