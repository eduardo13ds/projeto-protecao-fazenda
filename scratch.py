# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
import time
import random

# Constantes ajustáveis (você pode calibrar estes valores com base em observações)
# Umidade
UMIDADE_BAIXA = 60  # Abaixo disso, probabilidade é muito baixa
UMIDADE_MEDIA = 75  # Acima disso, começamos a considerar possibilidade de chuva
UMIDADE_ALTA = 85  # Acima disso, alta probabilidade
UMIDADE_MUITO_ALTA = 90  # Acima disso, probabilidade muito alta

# Temperatura
QUEDA_TEMP_LEVE = 1.5  # Queda de temperatura em °C em período curto
QUEDA_TEMP_MEDIA = 3  # Queda significativa
QUEDA_TEMP_FORTE = 5  # Queda muito significativa

# Campo magnético/elétrico (os valores exatos dependerão da calibração do seu sensor)
VARIACAO_CAMPO_LEVE = 5  # Variação pequena, pouco significativa
VARIACAO_CAMPO_MEDIA = 15  # Variação moderada, pode indicar mudanças
VARIACAO_CAMPO_FORTE = 30  # Variação forte, possível tempestade se aproximando

# Período de medição (em minutos)
PERIODO_ANALISE = 30  # Intervalo de tempo entre medições para análise de tendências


def prever_chuva(umidade_atual, temperatura_atual, campo_atual,
                 umidade_anterior, temperatura_anterior, campo_anterior,
                 taxa_variacao_umidade=None):
    """
    Analisa os dados dos sensores e retorna a probabilidade de chuva

    Args:
        umidade_atual: Valor atual da umidade (%)
        temperatura_atual: Valor atual da temperatura (°C)
        campo_atual: Valor atual do campo magnético/elétrico
        umidade_anterior: Valor anterior da umidade (%)
        temperatura_anterior: Valor anterior da temperatura (°C)
        campo_anterior: Valor anterior do campo magnético/elétrico
        taxa_variacao_umidade: Taxa de aumento da umidade por hora (opcional)

    Returns:
        probabilidade: String indicando a probabilidade ("Muito Baixa", "Baixa", "Média", "Alta", "Muito Alta")
        razoes: Lista de razões que justificam a previsão
        tempo_estimado: Estimativa de tempo até a chuva (se houver indícios suficientes)
    """
    # Inicialização
    pontuacao = 0  # Sistema de pontuação para determinar probabilidade
    razoes = []
    tempo_estimado = None

    # Calcular variações
    variacao_umidade = umidade_atual - umidade_anterior
    variacao_temperatura = temperatura_anterior - temperatura_atual  # Invertido para ser positivo em caso de queda
    variacao_campo = abs(campo_atual - campo_anterior)  # Valor absoluto da variação

    # 1. Análise da Umidade (fator mais importante)
    if umidade_atual >= UMIDADE_MUITO_ALTA:
        pontuacao += 4
        razoes.append(f"Umidade muito alta: {umidade_atual}%")
    elif umidade_atual >= UMIDADE_ALTA:
        pontuacao += 3
        razoes.append(f"Umidade alta: {umidade_atual}%")
    elif umidade_atual >= UMIDADE_MEDIA:
        pontuacao += 2
        razoes.append(f"Umidade moderada: {umidade_atual}%")
    elif umidade_atual < UMIDADE_BAIXA:
        pontuacao -= 2
        razoes.append(f"Umidade baixa: {umidade_atual}%")

    # Analisar tendência de umidade
    if variacao_umidade > 0:
        if variacao_umidade >= 5:
            pontuacao += 2
            razoes.append(f"Aumento rápido de umidade: +{variacao_umidade}%")
        else:
            pontuacao += 1
            razoes.append(f"Aumento de umidade: +{variacao_umidade}%")

    # 2. Análise da Temperatura
    if variacao_temperatura >= QUEDA_TEMP_FORTE:
        pontuacao += 3
        razoes.append(f"Queda brusca de temperatura: {variacao_temperatura}°C")
        tempo_estimado = "1-2 horas"
    elif variacao_temperatura >= QUEDA_TEMP_MEDIA:
        pontuacao += 2
        razoes.append(f"Queda significativa de temperatura: {variacao_temperatura}°C")
        tempo_estimado = "2-4 horas"
    elif variacao_temperatura >= QUEDA_TEMP_LEVE:
        pontuacao += 1
        razoes.append(f"Leve queda de temperatura: {variacao_temperatura}°C")

    # 3. Análise do Campo Magnético/Elétrico
    if variacao_campo >= VARIACAO_CAMPO_FORTE:
        pontuacao += 4
        razoes.append(f"Alteração muito significativa no campo magnético: {variacao_campo}")
        tempo_estimado = "Possível tempestade em breve (1 hora ou menos)"
    elif variacao_campo >= VARIACAO_CAMPO_MEDIA:
        pontuacao += 2
        razoes.append(f"Alteração moderada no campo magnético: {variacao_campo}")
    elif variacao_campo >= VARIACAO_CAMPO_LEVE:
        pontuacao += 1
        razoes.append(f"Pequena alteração no campo magnético: {variacao_campo}")

    # 4. Combinações especiais (efeitos sinérgicos)
    if umidade_atual >= UMIDADE_ALTA and variacao_temperatura >= QUEDA_TEMP_MEDIA:
        pontuacao += 2
        razoes.append("Combinação de umidade alta e queda de temperatura")

    if umidade_atual >= UMIDADE_MEDIA and variacao_campo >= VARIACAO_CAMPO_MEDIA:
        pontuacao += 2
        razoes.append("Combinação de umidade elevada e alteração no campo magnético")

    if variacao_campo >= VARIACAO_CAMPO_MEDIA and variacao_temperatura >= QUEDA_TEMP_MEDIA:
        pontuacao += 3
        razoes.append("Combinação de alteração no campo magnético e queda de temperatura")
        if tempo_estimado is None or "tempestade" not in tempo_estimado:
            tempo_estimado = "Provável precipitação em 1-3 horas"

    # 5. Análise da taxa de aumento de umidade (se disponível)
    if taxa_variacao_umidade is not None and taxa_variacao_umidade > 0:
        if taxa_variacao_umidade >= 10:  # 10% por hora
            pontuacao += 3
            razoes.append(f"Rápido aumento na taxa de umidade: {taxa_variacao_umidade}% por hora")
        elif taxa_variacao_umidade >= 5:  # 5% por hora
            pontuacao += 2
            razoes.append(f"Aumento significativo na taxa de umidade: {taxa_variacao_umidade}% por hora")

    # Determinar probabilidade baseada na pontuação
    if pontuacao >= 10:
        probabilidade = "Muito Alta"
        if tempo_estimado is None:
            tempo_estimado = "Precipitação iminente (menos de 2 horas)"
    elif pontuacao >= 7:
        probabilidade = "Alta"
        if tempo_estimado is None:
            tempo_estimado = "Possível precipitação em 2-4 horas"
    elif pontuacao >= 4:
        probabilidade = "Média"
        if tempo_estimado is None:
            tempo_estimado = "Possível precipitação nas próximas 4-8 horas"
    elif pontuacao >= 1:
        probabilidade = "Baixa"
        tempo_estimado = None  # Sem estimativa confiável
    else:
        probabilidade = "Muito Baixa"
        tempo_estimado = None
        razoes.append("Nenhum indicador significativo de precipitação")

    return probabilidade, razoes, tempo_estimado

umidade_anterior = None
temperatura_anterior = None
campo_anterior = None

while True:
    # Simulação da leitura do sensor Hall
    valor_sensorh = random.randint(-100, 100)
    print("Valor sensor Hall:", valor_sensorh)

    # Simulação da leitura do DHT22
    temperatura = round(random.uniform(20.0, 30.0), 2)
    print("Temperatura:", temperatura)

    umidade = round(random.uniform(40.0, 60.0), 2)
    print("Umidade:", umidade)

    # Verificar se há valores anteriores para realizar a previsão
    if umidade_anterior is not None and temperatura_anterior is not None and campo_anterior is not None:
        probabilidade, razoes, tempo_estimado = prever_chuva(
            umidade_atual=umidade,
            temperatura_atual=temperatura,
            campo_atual=valor_sensorh,
            umidade_anterior=umidade_anterior,
            temperatura_anterior=temperatura_anterior,
            campo_anterior=campo_anterior
        )
        print("Probabilidade de chuva:", probabilidade)
        print("Razões:", razoes)
        print("Tempo estimado:", tempo_estimado)
    else:
        print("Aguardando valores anteriores para realizar a previsão...")

    # Atualizar os valores anteriores
    umidade_anterior = umidade
    temperatura_anterior = temperatura
    campo_anterior = valor_sensorh

    # Encapsulando as variáveis em JSON
    dados = {
        "valor_sensor_hall": valor_sensorh,
        "temperatura": temperatura,
        "humidade": umidade,
        "probabilidade": probabilidade if 'probabilidade' in locals() else "Indefinida"
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
