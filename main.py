# -*- coding: utf-8 -*-
import umqtt.simple as mqtt  # Biblioteca para MQTT em MicroPython # type: ignore
import ujson  # Biblioteca para manipulação de JSON em MicroPython # type: ignore
import esp32 # type: ignore
from machine import Pin # type: ignore
import time

# Configuração do sensor Hall
sensor_hall = Pin(34, Pin.IN)  # GPIO 34 como entrada
# Configuração do DHT22
sensor_dht = Pin(32, Pin.IN)  # GPIO 32 como entrada

# Calibração inicial
def calibrar_sensor(amostras=20):
    print("Calibrando sensor Hall...")
    valores = []
    for _ in range(amostras):
        valores.append(esp32.hall_sensor())
        time.sleep(0.1)
    baseline = sum(valores) / len(valores)
    print("Valor base:", baseline)
    return baseline

# Inicialização
valor_base = calibrar_sensor()
ultimo_valor = valor_base

print("Monitorando campo magnético...")

while True:
    # Leitura do sensor Hall
    valor_sensorh = esp32.hall_sensor()
    print("Valor sensor Hall:", valor_sensorh)

    # Leitura do DHT22 (simulação)
    temperatura = sensor_dht.temperature()
    print("Temperatura:", temperatura)

    humidade = sensor_dht.humidity()
    print("Humidade:", humidade)

    # Encapsulando as variáveis em JSON

    dados = {
        "valor_sensor_hall": valor_sensorh,
        "temperatura": temperatura,
        "humidade": humidade
    }

    json_dados = ujson.dumps(dados)

    # Configuração do MQTT

    # Define the on_connect callback
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Conectado ao HiveMQ com sucesso!")
        else:
            print(f"Falha na conexão. Código de retorno: {rc}")

    # Define the on_publish callback
    def on_publish(client, userdata, mid):
        print(f"Mensagem publicada com ID: {mid}")

    # client_id is the given name of the client
    client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_publish = on_publish

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set("hivemq.webclient.1743567366904", "02DGadKA1Bb3fcCg.,;&")
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect("8ecd1811af00401b9570971ba2df918d.s1.eu.hivemq.cloud", 8883)

    # Start the MQTT client loop
    client.loop_start()

    # Publish the JSON data to a topic
    topic = "sensor/dados"
    result = client.publish(topic, json_dados, qos=1)

    # Wait for the message to be published
    result.wait_for_publish()

    print("Dados publicados no HiveMQ:", json_dados)

    time.sleep(10)  # Intervalo entre leituras
