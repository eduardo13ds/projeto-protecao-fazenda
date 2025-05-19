import json

import paho.mqtt.client as mqtt
from flask import Flask, render_template, jsonify

app = Flask(__name__)

latest_data = {}


# Variável global para armazenar os dados mais recentes do sensor. Inicializada como um dicionário vazio.
# Configuração MQTT
def on_connect(client, userdata, flags, rc, properties=None):
    # Função de callback chamada quando o cliente MQTT se conecta ao broker.
    if rc == 0:
        print("Conectado ao HiveMQ com sucesso!")  # Imprime uma mensagem de sucesso se a conexão for bem-sucedida.
        client.subscribe("sensor/dados")  # Se inscreve no tópico "sensor/dados" para receber mensagens.
    else:
        print(
            f"Falha na conexão. Código de retorno: {rc}")  # Imprime uma mensagem de erro se a conexão falhar, incluindo o código de retorno.


def on_message(client, userdata, msg):
    # Função de callback chamada quando uma mensagem é recebida no tópico inscrito.
    global latest_data
    latest_data = json.loads(
        msg.payload.decode())  # Decodifica a carga da mensagem (que é um JSON) e atualiza a variável global latest_data.
    print("Dados recebidos via MQTT:", latest_data)  # Imprime os dados recebidos via MQTT.


client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
# Cria um cliente MQTT com um ID de cliente vazio, sem dados do usuário e usando o protocolo MQTT versão 5.
client.on_connect = on_connect
# Define a função on_connect como a função de callback para o evento de conexão.
client.on_message = on_message
# Define a função on_message como a função de callback para o evento de recebimento de mensagem.

# Habilita TLS para uma conexão segura.
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
# Define a versão do protocolo TLS.

# Define o nome de usuário e senha para autenticação no broker MQTT.
client.username_pw_set("hivemq.webclient.1743567366904", "02DGadKA1Bb3fcCg.,;&")
# Conecta-se ao HiveMQ Cloud na porta 8883 (padrão para MQTT).
client.connect("fd2522b769fc4f16bb479a6cac3dcb7b.s1.eu.hivemq.cloud", 8883)
client.loop_start()


# Inicia um loop em segundo plano para lidar com a comunicação MQTT.
@app.route('/')
def index():
    # Define a rota para a página inicial ("/").
    return render_template('index.html', data=latest_data)


# Renderiza o template "index.html" passando os dados mais recentes do sensor para o template.

@app.route('/latest-data', methods=['GET'])
def latest_data_endpoint():
    # Define a rota para obter os dados mais recentes via requisição GET ("/latest-data").
    return jsonify(latest_data)


# Retorna os dados mais recentes do sensor em formato JSON.
if __name__ == '__main__':
    app.run(debug=True)
