"""
MQTT client module for handling MQTT connections and message processing.
"""

import json
import ssl
import paho.mqtt.client as mqtt

# Global variable to store the latest data received from MQTT, organized by area
latest_data_by_area = {}
latest_data = {}  # Manter para compatibilidade
latest_inmet_data = {}  # Novo: armazena o último dado do INMET

class MQTTClient:
    """MQTT client for connecting to a broker and handling messages."""
    
    def __init__(self, app=None):
        """Initialize the MQTT client.
        
        Args:
            app: Flask application instance. If provided, the client will be initialized.
        """
        self.client = None
        self.app = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the MQTT client with the Flask application.
        
        Args:
            app: Flask application instance.
        """
        self.app = app
        
        # Create MQTT client
        self.client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        # Enable TLS for secure connection
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        
        # Set username and password from configuration
        self.client.username_pw_set(
            app.config['MQTT_USERNAME'],
            app.config['MQTT_PASSWORD']
        )
        
        # Connect to the broker
        try:
            self.client.connect(
                app.config['MQTT_BROKER'],
                app.config['MQTT_PORT']
            )
            self.client.loop_start()
        except Exception as e:
            app.logger.error(f"Failed to connect to MQTT broker: {e}")

    def _on_connect(self, client, userdata, flags, reasonCode, properties=None):
        """Callback for when the client receives a CONNACK response from the server."""
        if self.app:
            self.app.logger.info("Connected to MQTT broker with reason code: %s", reasonCode)
            
        # Inscrever-se no tópico para receber dados dos sensores
        client.subscribe("sensor/dados", qos=0)
        if self.app:
            self.app.logger.info("Inscrito no tópico 'sensor/dados'")
        # Novo: inscreve também no tópico do INMET
        client.subscribe("inmet/dados", qos=0)
        if self.app:
            self.app.logger.info("Inscrito no tópico 'inmet/dados'")

    def _on_message(self, client, userdata, msg):
        """Callback for when a message is received from the broker."""
        global latest_data, latest_data_by_area, latest_inmet_data
        try:
            print(f"Mensagem recebida do tópico: {msg.topic}")
            data = json.loads(msg.payload.decode())
            print(f"Dados recebidos: {data}")

            if msg.topic == "inmet/dados":
                latest_inmet_data = data
                print(f"Dado INMET armazenado: {data}")
                if self.app:
                    self.app.logger.debug(f"INMET data received via MQTT: {data}")
                return

            # Armazenar os dados mais recentes (para compatibilidade)
            latest_data = data
    
            # Se o dado tiver uma área definida, armazená-lo por área
            if 'area' in data:
                area_id = data['area']
                latest_data_by_area[area_id] = data
                print(f"Dados da área {area_id} armazenados: {data}")
            
            if self.app:
                self.app.logger.debug(f"Data received via MQTT: {data}")
        except Exception as e:
            print(f"Erro ao processar mensagem MQTT: {e}")
            if self.app:
                self.app.logger.error(f"Error processing MQTT message: {e}")

    def get_all_latest_data(self):
        """Get all latest data received from MQTT, organized by area."""
        global latest_data_by_area
        return latest_data_by_area.copy()  # Retorna uma cópia para evitar modificações externas
    

    def get_latest_data(self, area_id=None):
        """Get the latest data received from MQTT.

        Args:
            area_id (int, optional): ID da área para filtrar os dados. Se não for fornecido,
                                    retorna os dados mais recentes de qualquer área.

        Returns:
            dict: The latest data received from MQTT.
        """
        global latest_data, latest_data_by_area

        if area_id is not None:
            try:
                return latest_data_by_area.get(int(area_id), {})
            except ValueError:
                print(f"Erro: ID da área '{area_id}' não é um número válido.")
                if self.app:
                    self.app.logger.error(f"Invalid area ID: {area_id}")
                return {}

        return latest_data

    def get_latest_inmet_data(self):
        """Retorna o último dado recebido do INMET via MQTT."""
        global latest_inmet_data
        return latest_inmet_data

# Create a singleton instance
mqtt_client = MQTTClient()