import paho.mqtt.client as mqtt
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global variable to store the latest sensor data
latest_data = {}

# MQTT configuration
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Conectado ao HiveMQ com sucesso!")
        client.subscribe("sensor/dados")  # Subscribe to the topic
    else:
        print(f"Falha na conexão. Código de retorno: {rc}")

def on_message(client, userdata, msg):
    global latest_data
    latest_data = json.loads(msg.payload.decode())  # Update the global variable
    print("Dados recebidos via MQTT:", latest_data)

client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set("hivemq.webclient.1743567366904", "02DGadKA1Bb3fcCg.,;&")
client.connect("8ecd1811af00401b9570971ba2df918d.s1.eu.hivemq.cloud", 8883)
client.loop_start()

@app.route('/')
def index():
    return render_template('index.html', data=latest_data)

@app.route('/update', methods=['POST'])
def update_data():
    global latest_data
    latest_data = request.json  # Update the global variable with the new data
    print("Dados recebidos:", latest_data)
    return jsonify({"status": "success"})

@app.route('/latest-data', methods=['GET'])
def latest_data_endpoint():
    return jsonify(latest_data)

if __name__ == '__main__':
    app.run(debug=True)