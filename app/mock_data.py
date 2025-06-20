# app/mock_data.py
"""
Dados mock para demonstração dos gráficos de relatórios
Este arquivo fornece dados simulados quando não há dados suficientes no banco
"""

import random
from datetime import datetime, timedelta
import json

def get_mock_quick_stats():
    """Retorna estatísticas rápidas simuladas."""
    return {
        'total_alertas': random.randint(15, 50),
        'alertas_criticos': random.randint(2, 8),
        'sensores_ativos': random.randint(12, 24),
        'media_leituras': round(random.uniform(15.5, 35.2), 1)
    }

def get_mock_heatmap_data():
    """Retorna dados simulados para o mapa de calor."""
    areas = ['Central', 'Norte', 'Sul', 'Leste', 'Oeste']
    data = []

    for area in areas:
        alertas = random.randint(0, 15)
        trend = random.randint(-20, 25)

        data.append({
            'area': area,
            'alertas': alertas,
            'trend': trend
        })

    return data

def get_mock_alerts_timeline():
    """Retorna dados simulados para timeline de alertas."""
    now = datetime.now()
    labels = []
    values = []

    # Últimas 24 horas, intervalos de 2 horas
    for i in range(12):
        time_point = now - timedelta(hours=i*2)
        labels.insert(0, time_point.strftime('%d/%m %H:%M'))
        values.insert(0, random.randint(0, 8))

    return {
        'labels': labels,
        'values': values
    }

def get_mock_alerts_intensity():
    """Retorna dados simulados para intensidade de alertas."""
    intensidades = ['Leve', 'Moderado', 'Severo', 'Crítico']
    labels = []
    values = []

    for intensidade in intensidades:
        count = random.randint(1, 10)
        labels.append(intensidade)
        values.append(count)

    return {
        'labels': labels,
        'values': values
    }

def get_mock_sensor_readings():
    """Retorna dados simulados para leituras de sensores."""
    now = datetime.now()
    labels = []

    # Últimas 12 horas
    for i in range(12):
        time_point = now - timedelta(hours=i)
        labels.insert(0, time_point.strftime('%d/%m %H:%M'))

    datasets = [
        {
            'label': 'Temperatura (°C)',
            'data': [round(random.uniform(18, 35), 1) for _ in range(12)]
        },
        {
            'label': 'Umidade (%)',
            'data': [round(random.uniform(40, 85), 1) for _ in range(12)]
        },
        {
            'label': 'Pressão (hPa)',
            'data': [round(random.uniform(980, 1020), 1) for _ in range(12)]
        }
    ]

    return {
        'labels': labels,
        'datasets': datasets
    }

def get_mock_device_status():
    """Retorna dados simulados para status dos dispositivos."""
    return {
        'labels': ['Ativo', 'Inativo', 'Manutenção'],
        'values': [
            random.randint(8, 15),
            random.randint(1, 4),
            random.randint(0, 3)
        ]
    }

def get_mock_correlation_data():
    """Retorna dados simulados para correlação temperatura x umidade."""
    points = []

    for _ in range(50):
        # Simula correlação inversa entre temperatura e umidade
        temp = random.uniform(15, 40)
        # Umidade tende a ser maior quando temperatura é menor
        base_humidity = 100 - (temp * 1.5)
        humidity = max(20, min(95, base_humidity + random.uniform(-15, 15)))

        points.append({
            'x': round(temp, 1),
            'y': round(humidity, 1)
        })

    return {'points': points}

def get_mock_quality_data():
    """Retorna dados simulados para qualidade das leituras."""
    now = datetime.now()
    labels = []

    # Últimas 8 horas
    for i in range(8):
        time_point = now - timedelta(hours=i)
        labels.insert(0, time_point.strftime('%d/%m %H:%M'))

    confiavel = []
    ruido = []
    fora_faixa = []

    for _ in range(8):
        total = random.randint(50, 120)
        ruido_count = random.randint(0, 8)
        fora_faixa_count = random.randint(0, 5)
        confiavel_count = total - ruido_count - fora_faixa_count

        confiavel.append(max(0, confiavel_count))
        ruido.append(ruido_count)
        fora_faixa.append(fora_faixa_count)

    return {
        'labels': labels,
        'confiavel': confiavel,
        'ruido': ruido,
        'fora_faixa': fora_faixa
    }

def get_mock_fazendas():
    """Retorna lista de fazendas simuladas."""
    return [
        {'id': 1, 'nome': 'Fazenda São José'},
        {'id': 2, 'nome': 'Fazenda Boa Vista'},
        {'id': 3, 'nome': 'Fazenda Santa Maria'},
        {'id': 4, 'nome': 'Fazenda Nova Esperança'}
    ]

def get_mock_tipos_sensor():
    """Retorna tipos de sensor simulados."""
    return [
        {'id': 1, 'nome': 'Temperatura'},
        {'id': 2, 'nome': 'Umidade'},
        {'id': 3, 'nome': 'Pressão Atmosférica'},
        {'id': 4, 'nome': 'Velocidade do Vento'},
        {'id': 5, 'nome': 'Precipitação'},
        {'id': 6, 'nome': 'Radiação Solar'}
    ]

# Dados para simulação de tendências históricas
HISTORICAL_TRENDS = {
    'alertas_por_mes': [12, 18, 25, 31, 28, 22, 35, 42, 38, 29, 24, 20],
    'eficiencia_sensores': [92.5, 94.1, 91.8, 95.2, 93.7, 92.9, 94.8, 93.4, 95.1, 92.6, 94.3, 93.8],
    'uptime_dispositivos': [98.2, 97.8, 99.1, 98.7, 97.9, 98.5, 99.2, 98.1, 97.6, 98.9, 99.0, 98.4]
}

def get_mock_weather_patterns():
    """Retorna padrões climáticos simulados para análise avançada."""
    return {
        'precipitacao_mensal': [85, 120, 95, 45, 15, 5, 8, 12, 35, 65, 110, 95],
        'temperatura_media': [28, 29, 27, 24, 21, 19, 18, 20, 23, 25, 27, 28],
        'dias_criticos': [2, 4, 3, 1, 0, 0, 0, 1, 2, 3, 4, 3]
    }

def get_mock_alert_distribution():
    """Retorna distribuição de alertas por área e tipo."""
    areas = ['Central', 'Norte', 'Sul', 'Leste', 'Oeste']
    tipos = ['Chuva Intensa', 'Vento Forte', 'Temperatura Extrema', 'Umidade Crítica']

    distribution = {}
    for area in areas:
        distribution[area] = {}
        for tipo in tipos:
            distribution[area][tipo] = random.randint(0, 10)

    return distribution

def get_mock_prediction_accuracy():
    """Retorna dados de precisão das previsões do modelo."""
    last_30_days = []
    now = datetime.now()

    for i in range(30):
        date = now - timedelta(days=i)
        accuracy = random.uniform(75, 95)

        last_30_days.insert(0, {
            'date': date.strftime('%d/%m'),
            'accuracy': round(accuracy, 1),
            'predictions_made': random.randint(8, 25),
            'correct_predictions': random.randint(6, 23)
        })

    return last_30_days

def get_mock_sensor_health():
    """Retorna dados de saúde dos sensores."""
    sensors = [
        {'id': 1, 'nome': 'Sensor-Norte-01', 'type': 'Temperatura', 'health': 95, 'last_reading': '2 min'},
        {'id': 2, 'nome': 'Sensor-Norte-02', 'type': 'Umidade', 'health': 88, 'last_reading': '1 min'},
        {'id': 3, 'nome': 'Sensor-Sul-01', 'type': 'Pressão', 'health': 92, 'last_reading': '3 min'},
        {'id': 4, 'nome': 'Sensor-Central-01', 'type': 'Vento', 'health': 78, 'last_reading': '15 min'},
        {'id': 5, 'nome': 'Sensor-Leste-01', 'type': 'Chuva', 'health': 96, 'last_reading': '1 min'},
        {'id': 6, 'nome': 'Sensor-Oeste-01', 'type': 'Radiação', 'health': 85, 'last_reading': '5 min'}
    ]

    return sensors

def get_mock_comparative_analysis():
    """Retorna dados para análise comparativa entre períodos."""
    return {
        'current_period': {
            'total_alerts': 45,
            'critical_alerts': 8,
            'avg_temp': 26.5,
            'avg_humidity': 72.3,
            'rainfall': 125.5
        },
        'previous_period': {
            'total_alerts': 38,
            'critical_alerts': 6,
            'avg_temp': 25.1,
            'avg_humidity': 69.8,
            'rainfall': 98.2
        },
        'year_ago': {
            'total_alerts': 52,
            'critical_alerts': 12,
            'avg_temp': 27.8,
            'avg_humidity': 74.1,
            'rainfall': 156.3
        }
    }

# Função principal para obter todos os dados mock
def get_all_mock_data():
    """Retorna todos os dados mock em um dicionário."""
    return {
        'quick_stats': get_mock_quick_stats(),
        'heatmap': get_mock_heatmap_data(),
        'alerts_timeline': get_mock_alerts_timeline(),
        'alerts_intensity': get_mock_alerts_intensity(),
        'sensor_readings': get_mock_sensor_readings(),
        'device_status': get_mock_device_status(),
        'correlation': get_mock_correlation_data(),
        'quality': get_mock_quality_data(),
        'fazendas': get_mock_fazendas(),
        'tipos_sensor': get_mock_tipos_sensor(),
        'weather_patterns': get_mock_weather_patterns(),
        'alert_distribution': get_mock_alert_distribution(),
        'prediction_accuracy': get_mock_prediction_accuracy(),
        'sensor_health': get_mock_sensor_health(),
        'comparative_analysis': get_mock_comparative_analysis()
    }

# Configurações para personalizar a geração de dados
MOCK_CONFIG = {
    'use_realistic_correlations': True,  # Usar correlações realistas entre dados
    'add_seasonal_variations': True,     # Adicionar variações sazonais
    'include_anomalies': True,           # Incluir algumas anomalias nos dados
    'base_alert_frequency': 0.3,        # Frequência base de alertas (0.0 a 1.0)
    'sensor_reliability': 0.92          # Confiabilidade base dos sensores
}

def apply_realistic_variations(data, data_type):
    """Aplica variações realistas aos dados baseado no tipo."""
    if not MOCK_CONFIG['use_realistic_correlations']:
        return data

    if data_type == 'temperature':
        # Temperatura varia mais durante o dia
        hour = datetime.now().hour
        if 10 <= hour <= 16:  # Período mais quente
            data = [x + random.uniform(2, 5) for x in data]
        elif 22 <= hour or hour <= 6:  # Período mais frio
            data = [x - random.uniform(1, 3) for x in data]

    elif data_type == 'humidity':
        # Umidade tende a ser maior de manhã cedo e à noite
        hour = datetime.now().hour
        if 5 <= hour <= 8 or 18 <= hour <= 22:
            data = [min(95, x + random.uniform(5, 15)) for x in data]

    return data

def get_mock_export_summary():
    """Retorna dados de resumo para exportação."""
    return {
        'report_period': '7 dias',
        'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'total_data_points': random.randint(1500, 3000),
        'quality_score': round(random.uniform(85, 96), 1),
        'system_uptime': round(random.uniform(97, 99.5), 1),
        'alerts_resolved': random.randint(15, 30),
        'predictions_accuracy': round(random.uniform(82, 94), 1)
    }
