# -*- coding: utf-8 -*-
import json
import random
import time

import paho.mqtt.client as mqtt

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

# Corrente elétrica (mA) - representando o campo elétrico atmosférico
VARIACAO_CORRENTE_LEVE = 5  # Variação pequena, pouco significativa
VARIACAO_CORRENTE_MEDIA = 15  # Variação moderada, pode indicar mudanças
VARIACAO_CORRENTE_FORTE = 30  # Variação forte, possível tempestade se aproximando

# Período de medição (em minutos)
PERIODO_ANALISE = 30  # Intervalo de tempo entre medições para análise de tendências


def prever_chuva(umidade_atual, temperatura_atual, corrente_atual,
                 umidade_anterior, temperatura_anterior, corrente_anterior,
                 taxa_variacao_umidade=None):
    """
    Analisa os dados dos sensores e retorna a probabilidade de chuva em porcentagem

    Args:
        umidade_atual: Valor atual da umidade (%)
        temperatura_atual: Valor atual da temperatura (°C)
        corrente_atual: Valor atual da corrente elétrica (mA)
        umidade_anterior: Valor anterior da umidade (%)
        temperatura_anterior: Valor anterior da temperatura (°C)
        corrente_anterior: Valor anterior da corrente elétrica (mA)
        taxa_variacao_umidade: Taxa de aumento da umidade por hora (opcional)

    Returns:
        probabilidade: Inteiro indicando a probabilidade em porcentagem (0-100%)
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
    variacao_corrente = abs(corrente_atual - corrente_anterior)  # Valor absoluto da variação

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

    # 3. Análise da Corrente Elétrica (representando o campo elétrico atmosférico)
    if variacao_corrente >= VARIACAO_CORRENTE_FORTE:
        pontuacao += 4
        razoes.append(f"Alteração muito significativa na corrente elétrica: {variacao_corrente} mA")
        tempo_estimado = "Possível tempestade em breve (1 hora ou menos)"
    elif variacao_corrente >= VARIACAO_CORRENTE_MEDIA:
        pontuacao += 2
        razoes.append(f"Alteração moderada na corrente elétrica: {variacao_corrente} mA")
    elif variacao_corrente >= VARIACAO_CORRENTE_LEVE:
        pontuacao += 1
        razoes.append(f"Pequena alteração na corrente elétrica: {variacao_corrente} mA")

    # 4. Combinações especiais (efeitos sinérgicos)
    if umidade_atual >= UMIDADE_ALTA and variacao_temperatura >= QUEDA_TEMP_MEDIA:
        pontuacao += 2
        razoes.append("Combinação de umidade alta e queda de temperatura")

    if umidade_atual >= UMIDADE_MEDIA and variacao_corrente >= VARIACAO_CORRENTE_MEDIA:
        pontuacao += 2
        razoes.append("Combinação de umidade elevada e alteração na corrente elétrica")

    if variacao_corrente >= VARIACAO_CORRENTE_MEDIA and variacao_temperatura >= QUEDA_TEMP_MEDIA:
        pontuacao += 3
        razoes.append("Combinação de alteração na corrente elétrica e queda de temperatura")
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
        probabilidade_percent = 100
        if tempo_estimado is None:
            tempo_estimado = "Precipitação iminente (menos de 2 horas)"
    elif 7 <= pontuacao < 10:
        probabilidade_percent = 80 + (pontuacao - 7) * (20 / 3)
    elif 4 <= pontuacao < 7:
        probabilidade_percent = 60 + (pontuacao - 4) * (20 / 3)
    elif 1 <= pontuacao < 4:
        probabilidade_percent = 40 + (pontuacao - 1) * (20 / 3)
    else:
        probabilidade_percent = 20 if pontuacao >= 0 else 0

    probabilidade_percent = round(probabilidade_percent)
    probabilidade = max(0, min(100, probabilidade_percent))  # Garantir que esteja entre 0 e 100

    # Adicionar razão se não houver indicadores
    if probabilidade <= 20 and not razoes:
        razoes.append("Nenhum indicador significativo de precipitação")

    return probabilidade, razoes, tempo_estimado


umidade_anterior = None
temperatura_anterior = None
corrente_anterior = None

# Adicionando lógica para enviar alerta ao MQTT em caso de probabilidade alta de chuva ou aumento imprevisível

while True:
    # Simulação da leitura do potenciômetro (ADC)
    adc_value = random.randint(0, 4095)  # Valor de 12 bits (0-4095)

    # Conversão para tensão
    voltage = (adc_value * 3.3) / 4095

    # Cálculo da corrente (Lei de Ohm)
    R = 100  # 100 Ohms
    current = voltage / R
    current_mA = current * 1000  # Converte para miliamperes

    print("ADC:", adc_value, "| Tensão:", round(voltage, 3), "V | Corrente:", round(current_mA, 2), "mA")

    # Simulação da leitura do DHT22
    temperatura = round(random.uniform(20.0, 30.0), 2)
    print("Temperatura:", temperatura)

    umidade = round(random.uniform(40.0, 60.0), 2)
    print("Umidade:", umidade)

    # Verificar se há valores anteriores para realizar a previsão
    if umidade_anterior is not None and temperatura_anterior is not None and corrente_anterior is not None:
        probabilidade, razoes, tempo_estimado = prever_chuva(
            umidade_atual=umidade,
            temperatura_atual=temperatura,
            corrente_atual=current_mA,
            umidade_anterior=umidade_anterior,
            temperatura_anterior=temperatura_anterior,
            corrente_anterior=corrente_anterior
        )
        print("Probabilidade de chuva:", probabilidade)
        print("Razões:", razoes)
        print("Tempo estimado:", tempo_estimado)

        # Enviar alerta ao MQTT se a probabilidade for alta ou muito alta
        if probabilidade in ["Alta", "Muito Alta"] or any("significativa" in razao for razao in razoes):
            alerta = {
                "alerta": "Condições críticas detectadas!",
                "probabilidade": probabilidade,
                "razoes": razoes,
                "tempo_estimado": tempo_estimado
            }
            alerta_json = json.dumps(alerta)
            client.publish("sensor/alertas", alerta_json, qos=1)
            print("Alerta enviado ao MQTT:", alerta_json)
    else:
        print("Aguardando valores anteriores para realizar a previsão...")

    # Atualizar os valores anteriores
    umidade_anterior = umidade
    temperatura_anterior = temperatura
    corrente_anterior = current_mA

    # Encapsulando as variáveis em JSON
    dados = {
        "adc_value": adc_value,
        "voltage": voltage,
        "current_mA": round(current_mA, 2),
        "temperatura": temperatura,
        "humidade": umidade,
        "probabilidade": probabilidade if 'probabilidade' in locals() else "Indefinida",
        "razoes": razoes if 'razoes' in locals() else [],
    }

    json_dados = json.dumps(dados, ensure_ascii=False)


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
    result.wait_for_publish()

    print("Dados publicados no HiveMQ:", json_dados)

    time.sleep(10)  # Intervalo entre leituras
