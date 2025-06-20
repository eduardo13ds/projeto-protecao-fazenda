import datetime
import random
import numpy as np
import os

# --- CONFIGURAÇÕES GERAIS ---
OUTPUT_SQL_FILE = 'leituras_simuladas_junho_2025.sql'
DIAS_PARA_GERAR = 16

# IDs dos sensores que serão simulados, conforme o schema do banco de dados
SENSOR_IDS = {
    'pressao': 1,
    'ponto_orvalho': 41,
    'vento_velocidade': 42,
    'vento_direcao': 43,
    'vento_rajada': 44,
    'radiacao_solar': 45,
    'precipitacao': 46,
    'temperatura': 9,
    'umidade': 4,
}

# --- PARÂMETROS DA SIMULAÇÃO (AJUSTADOS PARA CURITIBA EM JUNHO) ---
BASE_TEMP = 13.0  # Temperatura média
TEMP_AMPLITUDE = 6.0  # Variação de temperatura durante o dia
BASE_HUMIDITY = 85.0  # Umidade média
BASE_PRESSURE = 1020.0 # Pressão atmosférica média
CHANCE_DE_CHUVA = 0.10 # 10% de chance de chover em uma dada hora

def gerar_dados_simulados():
    """
    Função principal que gera os dados simulados e escreve o arquivo SQL.
    """
    # Determina o intervalo de datas: os últimos 15 dias do mês atual
    hoje = datetime.date(2025, 6, 1) # Usando a data de referência
    ultimo_dia_mes = datetime.date(hoje.year, hoje.month + 1, 1) - datetime.timedelta(days=1)
    data_inicio = ultimo_dia_mes - datetime.timedelta(days=DIAS_PARA_GERAR - 1)

    lista_de_queries = []

    print(f"Gerando dados de {data_inicio.strftime('%d/%m/%Y')} a {ultimo_dia_mes.strftime('%d/%m/%Y')}...")

    # Itera sobre cada dia no intervalo
    for dia_offset in range(DIAS_PARA_GERAR):
        data_atual = data_inicio + datetime.timedelta(days=dia_offset)

        # Adiciona uma variação diária para temperatura e pressão
        variacao_temp_dia = random.uniform(-1.5, 1.5)
        pressao_diaria = BASE_PRESSURE + random.uniform(-5, 5)

        # Itera sobre cada hora do dia
        for hora in range(24):
            timestamp = datetime.datetime(data_atual.year, data_atual.month, data_atual.day, hora)

            # --- GERAÇÃO DOS VALORES ---

            # Temperatura: simula um ciclo diário (mais frio à noite, mais quente à tarde)
            temp = (BASE_TEMP + variacao_temp_dia -
                    TEMP_AMPLITUDE * np.cos(2 * np.pi * (hora - 14) / 24) +
                    random.uniform(-0.5, 0.5))

            # Umidade: geralmente inversamente proporcional à temperatura
            umidade = (BASE_HUMIDITY + (temp - BASE_TEMP) * -2.5 + random.uniform(-5, 5))
            umidade = max(50, min(100, umidade)) # Limita entre 50% e 100%

            # Pressão: varia suavemente ao longo do dia
            pressao = pressao_diaria + random.uniform(-0.3, 0.3)

            # Precipitação: chance pequena de ocorrer chuva
            precipitacao = 0.0
            if random.random() < CHANCE_DE_CHUVA:
                precipitacao = round(random.uniform(0.1, 3.5), 1)
                # Quando chove, a umidade sobe e a temperatura cai um pouco
                umidade = min(100, umidade + 10)
                temp -= 1.0

            # Radiação Solar: segue a curva do sol (zero à noite)
            radiacao = 0.0
            if 6 <= hora <= 18:
                radiacao = (2500 * np.sin(np.pi * (hora - 6) / 12) + random.uniform(-50, 50))
                radiacao = max(0, radiacao)
                if precipitacao > 0: # Menos radiação com chuva
                    radiacao *= 0.3

            # Vento
            vento_velocidade = random.uniform(0.5, 4.0)
            vento_rajada = vento_velocidade + random.uniform(0, 5.0)
            vento_direcao = random.randint(0, 359)

            # Ponto de Orvalho (cálculo simplificado)
            ponto_orvalho = temp - ((100 - umidade) / 5.0)

            # --- MONTAGEM DA QUERY ---
            valores = {
                'temperatura': round(temp, 1),
                'umidade': round(umidade, 1),
                'pressao': round(pressao, 1),
                'precipitacao': precipitacao,
                'radiacao_solar': round(radiacao, 2),
                'vento_velocidade': round(vento_velocidade, 1),
                'vento_rajada': round(vento_rajada, 1),
                'vento_direcao': vento_direcao,
                'ponto_orvalho': round(ponto_orvalho, 1)
            }

            ts_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            for nome_sensor, valor in valores.items():
                id_sensor = SENSOR_IDS[nome_sensor]
                query = (
                    f"INSERT INTO `registro_leituras` "
                    f"(`ID_Sensor`, `Valor_Leitura`, `Timestamp_Leitura`, `Qualidade`) "
                    f"VALUES ({id_sensor}, '{valor}', '{ts_str}', 'Confiavel');"
                )
                lista_de_queries.append(query)

    # --- ESCRITA DO ARQUIVO SQL ---
    with open(OUTPUT_SQL_FILE, 'w', encoding='utf-8') as f:
        f.write("-- ====================================================================\n")
        f.write(f"-- Script SQL gerado dinamicamente por Python em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"-- Contém dados simulados para o período de {data_inicio.strftime('%d/%m/%Y')} a {ultimo_dia_mes.strftime('%d/%m/%Y')}.\n")
        f.write("-- Total de registros: " + str(len(lista_de_queries)) + "\n")
        f.write("-- ====================================================================\n\n")
        f.write("\n".join(lista_de_queries))
        f.write("\n\n-- Fim do script de simulação.\n")

    print(f"\nSucesso! O arquivo '{OUTPUT_SQL_FILE}' foi gerado no diretório '{os.getcwd()}'")
    print(f"Ele contém {len(lista_de_queries)} comandos INSERT prontos para serem executados.")


# --- Executa a função principal ---
gerar_dados_simulados()
