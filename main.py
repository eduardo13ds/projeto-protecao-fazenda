# -*- coding: utf-8 -*-
import time

import dht
import ujson  # Biblioteca para manipulação de JSON em MicroPython # type: ignore
import umqtt.simple as mqtt  # Biblioteca para MQTT em MicroPython # type: ignore
from machine import ADC, Pin  # type: ignore

# Configuração do DHT22

sensor_dht = dht.DHT11(Pin(18))  # GPIO 18 para o DHT11

# Configuração do potenciômetro (GPIO2)
pot = ADC(Pin(2))
pot.atten(ADC.ATTN_11DB)  # Faixa de 0-3.3V

# Valor do resistor de carga
R = 100  # 100 Ohms

print("Iniciando monitoramento...")

while True:
    print("Tudo ocorrendo perfeitamente :D")

    # Leitura do ADC (12 bits = 0-4095)
    adc_value = pot.read()

    # Conversão para tensão
    voltage = (adc_value * 3.3) / 4095

    # Cálculo da corrente (Lei de Ohm)
    current = voltage / R
    current_mA = current * 1000  # Converte para miliamperes

    # Exibição dos resultados
    print(f"ADC: {adc_value:4d} | Tensão: {voltage:.3f}V | Corrente: {current_mA:.2f}mA")

    # Leitura do DHT22 (simulação)
    temperatura = sensor_dht.temperature()
    print("Temperatura:", temperatura)

    humidade = sensor_dht.humidity()
    print("Humidade:", humidade)

    # Encapsulando as variáveis em JSON
    dados = {
        "adc_value": adc_value,
        "voltage": voltage,
        "current_mA": current_mA,
        "valor_sensor_hall": current_mA,  # Mantendo compatibilidade com o frontend
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
    client.connect("fd2522b769fc4f16bb479a6cac3dcb7b.s1.eu.hivemq.cloud", 8883)

    # Start the MQTT client loop
    client.loop_start()

    # Publish the JSON data to a topic
    topic = "sensor/dados"
    result = client.publish(topic, json_dados, qos=1)

    # Wait for the message to be published
    result.wait_for_publish()

    print("Dados publicados no HiveMQ:", json_dados)

    time.sleep(10)  # Intervalo entre leituras
