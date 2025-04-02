# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
import time
import random

while True:
    # Simulação da leitura do sensor Hall
    valor_sensorh = random.randint(-100, 100)
    print("Valor sensor Hall:", valor_sensorh)

    # Simulação da leitura do DHT22
    temperatura = round(random.uniform(20.0, 30.0), 2)
    print("Temperatura:", temperatura)

    humidade = round(random.uniform(40.0, 60.0), 2)
    print("Humidade:", humidade)

    # Encapsulando as variáveis em JSON
    dados = {
        "valor_sensor_hall": valor_sensorh,
        "temperatura": temperatura,
        "humidade": humidade
    }

    json_dados = json.dumps(dados)

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
    result.wait_for_publish()

    print("Dados publicados no HiveMQ:", json_dados)

    time.sleep(10)  # Intervalo entre leituras
