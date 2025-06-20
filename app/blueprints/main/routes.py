"""
Routes for the main blueprint.
"""
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.mqtt.client import mqtt_client
from app.models.alerta import Alerta
from app.models.atuador import Atuador
from app.models.fazenda import Fazenda
from app.models.nivel_acesso import NivelAcesso
from app.models.registro_comando_atuador import RegistroComandoAtuador
from app.models.registro_leitura import RegistroLeitura
from app.models.sensor import Sensor
from app.models.tipo_atuador import TipoAtuador
from app.models.tipo_sensor import TipoSensor
from app.models.usuario import Usuario
from app.models.tabelas_associacao import usuario_fazenda_acesso
from app.ml_services import PredictionService
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import json
from app import mock_data


# Create blueprint
main = Blueprint('main', __name__)

# A simple mapping for area IDs to names for display purposes
AREA_NAMES = {
    1: "Central",
    2: "Norte",
    3: "Sul",
    4: "Leste",
    5: "Oeste",
}

@main.route('/')
@main.route('/<int:area_id>')
@login_required
def index(area_id=None):
    """Render the home page.

    Args:
        area_id (int, optional): ID da área a ser monitorada. Se não for fornecido,
                                mostra dados de todas as áreas.

    Returns:
        str: Rendered HTML template.
    """
    # Initial data for area name display in header
    current_area_name = None
    if area_id is not None:
        current_area_name = AREA_NAMES.get(area_id, f"Área {area_id}")
    else:
        # For the main page, JavaScript will handle fetching global or specific data.
        # The header might default to "Todas" or the first detected alert area by JS.
        current_area_name = "Todas"

    # The 'data' passed here is minimal. JavaScript handles the dynamic content.
    return render_template('index.html', current_area=area_id, current_area_name=current_area_name)

@main.route('/painel_alertas')
@login_required
def painel_alertas():
    """Render the alerts page."""
    return render_template('alertas.html')

@main.route('/latest-data', methods=['GET'])
@main.route('/latest-data/<int:area_id>', methods=['GET'])
def latest_data_endpoint(area_id=None):
    """Get the latest data from MQTT.

    Args:
        area_id (int, optional): ID da área a ser monitorada.
                                Se não for fornecido, retorna uma lista de todos os alertas ativos.

    Returns:
        Response: JSON response with the latest data for a specific area
                  or a list of active alerts.
    """
    # Check if user is authenticated for AJAX requests
    if not current_user.is_authenticated:
        # Check if this is an AJAX request (fetch API or XMLHttpRequest)
        if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            'application/json' in request.headers.get('Accept', '') or
            request.is_json):
            return jsonify({
                'status': 'error',
                'message': 'Usuário não autenticado'
            }), 401
        # For regular requests, redirect to login
        return redirect(url_for('login.login'))

    if area_id is not None:
        data = mqtt_client.get_latest_data(area_id)
        # Simulate if no specific data for an area, but keep structure
        if not data:
             data = {
                "adc_value": 0, "area": area_id, "current_mA": 0, "humidade": 0,
                "probabilidade": 0, "razoes": ["Sem dados para esta área."], "temperatura": 0, "voltage": 0
            }
        # print(f"Requisição para área {area_id}, retornando dados: {data}") # Debug
        return jsonify(data)
    else:
        # Return all active alerts
        all_data = mqtt_client.get_all_latest_data() # Assumes you add this method to MQTTClient
        active_alerts = []
        for area_data_id, data_item in all_data.items():
            # Define your condition for an "active alert"
            # For example, probability > 75
            if data_item and data_item.get("probabilidade", 0) > 75:
                # Ensure area is part of the data_item if not already
                if 'area' not in data_item and area_data_id is not None:
                    data_item['area'] = area_data_id
                active_alerts.append(data_item)

        # print(f"Requisição para todas as áreas, retornando alertas ativos: {active_alerts}") # Debug
        return jsonify(active_alerts) # Returns a list of alert objects


@main.route('/latest-inmet', methods=['GET'])
def latest_inmet_endpoint():
    """Retorna o último dado recebido do INMET via MQTT."""
    # Check if user is authenticated for AJAX requests
    if not current_user.is_authenticated:
        # Check if this is an AJAX request (fetch API or XMLHttpRequest)
        if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            'application/json' in request.headers.get('Accept', '') or
            request.is_json):
            return jsonify({
                'status': 'error',
                'message': 'Usuário não autenticado'
            }), 401
        # For regular requests, redirect to login
        return redirect(url_for('login.login'))

    data = mqtt_client.get_latest_inmet_data()

    return jsonify(data)
# Adicione outras rotas aqui (registro, etc.)

@main.route('/predict-precipitation')
@main.route('/predict-precipitation/<int:area_id>')
@login_required
def predict_precipitation_endpoint(area_id=None):
    """
    Endpoint para obter a previsão de precipitação do modelo de ML.
    """
    try:
        prediction = PredictionService.predict(area_id)
        if prediction is not None:
            prediction_text = f"{round(prediction, 1)} mm"
            return jsonify({
                'status': 'success',
                'predicted_precipitation': prediction_text,
                'raw_value': prediction  # Para uso no card highlighting
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Dados históricos insuficientes para fazer uma previsão.'
            }), 400
    except Exception as e:
        current_app.logger.error(f"Erro no endpoint de previsão: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Ocorreu um erro interno durante a previsão.'
        }), 500

@main.route('/predict_precipitation/')
@main.route('/predict_precipitation/<int:area_id>')
@login_required
def predict_precipitation(area_id=None):
    """Get precipitation prediction for a specific area or all areas."""
    try:
        current_app.logger.info(f"Requisição de previsão para área: {area_id}")
        
        prediction = PredictionService.predict(area_id)
        current_app.logger.info(f"Previsão calculada: {prediction}")
        
        if prediction is None:
            return jsonify({
                'status': 'error',
                'message': 'Não foi possível gerar previsão'
            }), 400
        
        return jsonify({
            'status': 'success',
            'predicted_precipitation': f"{prediction:.1f} mm",
            'raw_value': float(prediction)
        })
    except Exception as e:
        current_app.logger.error(f"Erro na previsão: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@main.route('/relatorios')
@login_required
def relatorios():
    """Render the reports page."""
    return render_template('relatorios.html')

# === ROTAS DA API DE RELATÓRIOS ===

@main.route('/api/reports/fazendas', methods=['GET'])
@login_required
def get_fazendas():
    """Retorna lista de fazendas para filtros."""
    try:
        from app.models.fazenda import Fazenda
        fazendas = Fazenda.query.all()
        if not fazendas:
            return jsonify(mock_data.get_mock_fazendas())
        return jsonify([{
            'id': f.id_fazenda,
            'nome': f.nome_fazenda
        } for f in fazendas])
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar fazendas: {e}")
        return jsonify(mock_data.get_mock_fazendas())

@main.route('/api/reports/tipos-sensor', methods=['GET'])
@login_required
def get_tipos_sensor():
    """Retorna lista de tipos de sensor para filtros."""
    try:
        tipos = TipoSensor.query.all()
        if not tipos:
            return jsonify(mock_data.get_mock_tipos_sensor())
        return jsonify([{
            'id': t.id_tipo_sensor,
            'nome': t.nome_tipo
        } for t in tipos])
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar tipos de sensor: {e}")
        return jsonify(mock_data.get_mock_tipos_sensor())

@main.route('/api/reports/quick-stats', methods=['POST'])
@login_required
def get_quick_stats():
    """Retorna estatísticas rápidas baseadas nos filtros."""
    try:
        filters = request.get_json()

        # Calcular período
        if filters['period'] == '24h':
            start_date = datetime.utcnow() - timedelta(hours=24)
        elif filters['period'] == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif filters['period'] == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)

        # Total de alertas
        alertas_query = Alerta.query.filter(Alerta.timestamp_emissao >= start_date)
        if filters['fazenda'] != 'all':
            alertas_query = alertas_query.filter(Alerta.id_fazenda == filters['fazenda'])
        total_alertas = alertas_query.count()

        # Alertas críticos
        alertas_criticos = alertas_query.filter(Alerta.intensidade == 'Critico').count()

        # Sensores ativos
        sensores_query = Sensor.query.filter(Sensor.status == 'Ativo')
        if filters['fazenda'] != 'all':
            sensores_query = sensores_query.join(Sensor.dispositivo).filter(
                Sensor.dispositivo.has(id_fazenda=filters['fazenda'])
            )
        sensores_ativos = sensores_query.count()

        # Média de leituras por hora
        leituras_query = RegistroLeitura.query.filter(RegistroLeitura.timestamp_leitura >= start_date)
        if filters['sensor'] != 'all':
            leituras_query = leituras_query.join(RegistroLeitura.sensor).filter(
                RegistroLeitura.sensor.has(id_tipo_sensor=filters['sensor'])
            )
        total_leituras = leituras_query.count()
        horas = (datetime.utcnow() - start_date).total_seconds() / 3600
        media_leituras = round(total_leituras / horas, 1) if horas > 0 else 0

        # Se não há dados suficientes, usar dados mock
        if total_alertas == 0 and sensores_ativos == 0:
            return jsonify(mock_data.get_mock_quick_stats())

        return jsonify({
            'total_alertas': total_alertas,
            'alertas_criticos': alertas_criticos,
            'sensores_ativos': sensores_ativos,
            'media_leituras': media_leituras
        })
    except Exception as e:
        current_app.logger.error(f"Erro ao calcular estatísticas: {e}")
        return jsonify(mock_data.get_mock_quick_stats())

@main.route('/api/reports/heatmap', methods=['POST'])
@login_required
def get_heatmap_data():
    """Retorna dados para o mapa de calor das áreas."""
    try:
        filters = request.get_json()

        # Calcular período
        if filters['period'] == '24h':
            start_date = datetime.utcnow() - timedelta(hours=24)
        elif filters['period'] == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif filters['period'] == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)

        # Simular dados de áreas (baseado nos dispositivos e alertas)
        areas_data = []
        area_names = ['Central', 'Norte', 'Sul', 'Leste', 'Oeste']

        for i, area_name in enumerate(area_names, 1):
            # Contar alertas por área (usando uma lógica simplificada)
            # Na prática, você teria uma relação mais direta entre área e alertas
            alertas = Alerta.query.filter(
                Alerta.timestamp_emissao >= start_date,
                func.mod(Alerta.id_alerta, 5) == (i - 1)  # Distribuição simulada
            ).count()

            # Calcular tendência (comparar com período anterior)
            prev_start = start_date - (datetime.utcnow() - start_date)
            prev_alertas = Alerta.query.filter(
                Alerta.timestamp_emissao >= prev_start,
                Alerta.timestamp_emissao < start_date,
                func.mod(Alerta.id_alerta, 5) == (i - 1)
            ).count()

            trend = 0
            if prev_alertas > 0:
                trend = round(((alertas - prev_alertas) / prev_alertas) * 100, 1)

            areas_data.append({
                'area': area_name,
                'alertas': alertas,
                'trend': trend
            })

        # Se não há dados suficientes, usar dados mock
        if not areas_data or all(item['alertas'] == 0 for item in areas_data):
            return jsonify(mock_data.get_mock_heatmap_data())

        return jsonify(areas_data)
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar mapa de calor: {e}")
        return jsonify(mock_data.get_mock_heatmap_data())

@main.route('/api/reports/alerts-timeline', methods=['POST'])
@login_required
def get_alerts_timeline():
    """Retorna dados para o gráfico de timeline de alertas."""
    try:
        filters = request.get_json()

        # Calcular período
        if filters['period'] == '24h':
            start_date = datetime.utcnow() - timedelta(hours=24)
            interval = timedelta(hours=1)
        elif filters['period'] == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
            interval = timedelta(hours=6)
        elif filters['period'] == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
            interval = timedelta(days=1)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)
            interval = timedelta(hours=6)

        # Gerar labels e valores
        labels = []
        values = []
        current_time = start_date

        while current_time <= datetime.utcnow():
            # Contar alertas no intervalo
            next_time = current_time + interval
            alertas_count = Alerta.query.filter(
                Alerta.timestamp_emissao >= current_time,
                Alerta.timestamp_emissao < next_time
            ).count()

            labels.append(current_time.strftime('%d/%m %H:%M'))
            values.append(alertas_count)
            current_time = next_time

        # Se não há dados suficientes, usar dados mock
        if not values or all(v == 0 for v in values):
            return jsonify(mock_data.get_mock_alerts_timeline())

        return jsonify({
            'labels': labels,
            'values': values
        })
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar timeline de alertas: {e}")
        return jsonify(mock_data.get_mock_alerts_timeline())

@main.route('/api/reports/alerts-intensity', methods=['POST'])
@login_required
def get_alerts_intensity():
    """Retorna dados para o gráfico de intensidade de alertas."""
    try:
        filters = request.get_json()

        # Calcular período
        if filters['period'] == '24h':
            start_date = datetime.utcnow() - timedelta(hours=24)
        elif filters['period'] == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif filters['period'] == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)

        # Contar por intensidade
        intensidades = ['Leve', 'Moderado', 'Severo', 'Critico']
        labels = []
        values = []

        for intensidade in intensidades:
            count = Alerta.query.filter(
                Alerta.timestamp_emissao >= start_date,
                Alerta.intensidade == intensidade
            ).count()
            if count > 0:
                labels.append(intensidade)
                values.append(count)

        # Se não há dados suficientes, usar dados mock
        if not labels or not values:
            return jsonify(mock_data.get_mock_alerts_intensity())

        return jsonify({
            'labels': labels,
            'values': values
        })
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar intensidade de alertas: {e}")
        return jsonify(mock_data.get_mock_alerts_intensity())

@main.route('/api/reports/sensor-readings', methods=['POST'])
@login_required
def get_sensor_readings():
    """Retorna dados para o gráfico de leituras dos sensores."""
    try:
        filters = request.get_json()

        # Calcular período
        if filters['period'] == '24h':
            start_date = datetime.utcnow() - timedelta(hours=24)
        elif filters['period'] == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif filters['period'] == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)

        # Buscar leituras agrupadas por hora
        query = func.date_trunc('hour', RegistroLeitura.timestamp_leitura).label('hora')

        readings = db.session.query(
            query,
            TipoSensor.nome_tipo,
            func.avg(RegistroLeitura.valor_numerico).label('media')
        ).join(
            RegistroLeitura.sensor
        ).join(
            Sensor.tipo_sensor
        ).filter(
            RegistroLeitura.timestamp_leitura >= start_date,
            RegistroLeitura.valor_numerico.isnot(None)
        ).group_by(
            query, TipoSensor.nome_tipo
        ).order_by(query).all()

        # Organizar dados por tipo de sensor
        data_by_type = {}
        labels = set()

        for reading in readings:
            hora = reading.hora.strftime('%d/%m %H:%M')
            tipo = reading.nome_tipo
            media = float(reading.media) if reading.media else 0

            if tipo not in data_by_type:
                data_by_type[tipo] = {}
            data_by_type[tipo][hora] = media
            labels.add(hora)

        # Converter para formato do Chart.js
        labels = sorted(list(labels))
        datasets = []

        for tipo, dados in data_by_type.items():
            dataset = {
                'label': tipo,
                'data': [dados.get(label, 0) for label in labels]
            }
            datasets.append(dataset)

        # Se não há dados suficientes, usar dados mock
        if not labels or not datasets:
            return jsonify(mock_data.get_mock_sensor_readings())

        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar leituras dos sensores: {e}")
        return jsonify(mock_data.get_mock_sensor_readings())

@main.route('/api/reports/device-status', methods=['POST'])
@login_required
def get_device_status():
    """Retorna dados para o gráfico de status dos dispositivos."""
    try:
        from app.models.dispositivo import Dispositivo

        status_counts = db.session.query(
            Dispositivo.status,
            func.count(Dispositivo.id_dispositivo)
        ).group_by(Dispositivo.status).all()

        labels = []
        values = []

        for status, count in status_counts:
            labels.append(status or 'Indefinido')
            values.append(count)

        # Se não há dados suficientes, usar dados mock
        if not labels or not values:
            return jsonify(mock_data.get_mock_device_status())

        return jsonify({
            'labels': labels,
            'values': values
        })
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar status dos dispositivos: {e}")
        return jsonify(mock_data.get_mock_device_status())

@main.route('/api/reports/correlation', methods=['POST'])
@login_required
def get_correlation_data():
    """Retorna dados para o gráfico de correlação."""
    try:
        filters = request.get_json()

        # Buscar leituras de temperatura e umidade
        temp_readings = db.session.query(
            RegistroLeitura.valor_numerico.label('temperatura'),
            RegistroLeitura.timestamp_leitura
        ).join(
            RegistroLeitura.sensor
        ).join(
            Sensor.tipo_sensor
        ).filter(
            TipoSensor.nome_tipo.ilike('%temperatura%'),
            RegistroLeitura.valor_numerico.isnot(None)
        ).subquery()

        umid_readings = db.session.query(
            RegistroLeitura.valor_numerico.label('umidade'),
            RegistroLeitura.timestamp_leitura
        ).join(
            RegistroLeitura.sensor
        ).join(
            Sensor.tipo_sensor
        ).filter(
            TipoSensor.nome_tipo.ilike('%umidade%'),
            RegistroLeitura.valor_numerico.isnot(None)
        ).subquery()

        # Juntar dados por timestamp próximo
        correlation_data = db.session.query(
            temp_readings.c.temperatura,
            umid_readings.c.umidade
        ).join(
            umid_readings,
            func.abs(
                func.extract('epoch', temp_readings.c.timestamp_leitura) -
                func.extract('epoch', umid_readings.c.timestamp_leitura)
            ) < 300  # 5 minutos de diferença
        ).limit(100).all()

        points = []
        for temp, umid in correlation_data:
            points.append({
                'x': float(temp),
                'y': float(umid)
            })

        # Se não há dados suficientes, usar dados mock
        if not points or len(points) < 10:
            return jsonify(mock_data.get_mock_correlation_data())

        return jsonify({'points': points})
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar correlação: {e}")
        return jsonify(mock_data.get_mock_correlation_data())

@main.route('/api/reports/quality', methods=['POST'])
@login_required
def get_quality_data():
    """Retorna dados para o gráfico de qualidade das leituras."""
    try:
        filters = request.get_json()

        # Calcular período
        if filters['period'] == '24h':
            start_date = datetime.utcnow() - timedelta(hours=24)
        elif filters['period'] == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif filters['period'] == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)

        # Buscar qualidade das leituras agrupadas por hora
        query = func.date_trunc('hour', RegistroLeitura.timestamp_leitura).label('hora')

        quality_data = db.session.query(
            query,
            RegistroLeitura.qualidade,
            func.count(RegistroLeitura.id_leitura).label('count')
        ).filter(
            RegistroLeitura.timestamp_leitura >= start_date
        ).group_by(
            query, RegistroLeitura.qualidade
        ).order_by(query).all()

        # Organizar dados
        data_by_quality = {'Confiavel': {}, 'Ruido': {}, 'Fora da Faixa': {}}
        labels = set()

        for reading in quality_data:
            hora = reading.hora.strftime('%d/%m %H:%M')
            qualidade = reading.qualidade or 'Confiavel'
            count = reading.count

            if qualidade in data_by_quality:
                data_by_quality[qualidade][hora] = count
                labels.add(hora)

        labels = sorted(list(labels))

        confiavel_data = [data_by_quality['Confiavel'].get(label, 0) for label in labels]
        ruido_data = [data_by_quality['Ruido'].get(label, 0) for label in labels]
        fora_faixa_data = [data_by_quality['Fora da Faixa'].get(label, 0) for label in labels]

        # Se não há dados suficientes, usar dados mock
        if not labels or all(v == 0 for v in confiavel_data + ruido_data + fora_faixa_data):
            return jsonify(mock_data.get_mock_quality_data())

        return jsonify({
            'labels': labels,
            'confiavel': confiavel_data,
            'ruido': ruido_data,
            'fora_faixa': fora_faixa_data
        })
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar qualidade das leituras: {e}")
        return jsonify(mock_data.get_mock_quality_data())

@main.route('/api/reports/export-full', methods=['POST'])
@login_required
def export_full_report():
    """Exporta relatório completo em PDF ou Excel."""
    try:
        data = request.get_json()
        format_type = data.get('format', 'pdf')

        if format_type == 'pdf':
            return _export_reports_pdf(data)
        elif format_type == 'excel':
            return _export_reports_excel(data)
        else:
            return jsonify({'error': 'Formato não suportado'}), 400

    except Exception as e:
        current_app.logger.error(f"Erro na exportação completa: {e}")
        return jsonify({'error': 'Erro interno na exportação'}), 500

def _export_reports_pdf(data):
    """Gera PDF do relatório completo."""
    from io import BytesIO
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    import base64
    from PIL import Image

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=60,
        title="Relatório Completo - StormGuard"
    )

    styles = getSampleStyleSheet()
    elements = []

    # Título
    title = Paragraph("<b>Relatório Completo de Análise - StormGuard</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Data/hora da geração
    now = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    date_para = Paragraph(f"<i>Gerado em: {now}</i>", styles['Normal'])
    elements.append(date_para)
    elements.append(Spacer(1, 30))

    # Adicionar gráficos como imagens
    charts = data.get('charts', [])
    for chart in charts:
        if chart.get('image'):
            try:
                # Decodificar imagem base64
                image_data = chart['image'].split(',')[1] if ',' in chart['image'] else chart['image']
                image_bytes = base64.b64decode(image_data)

                # Criar objeto de imagem
                img_buffer = BytesIO(image_bytes)
                img = RLImage(img_buffer, width=400, height=200)

                # Adicionar título do gráfico
                chart_title = Paragraph(f"<b>{chart['name'].replace('_', ' ').title()}</b>", styles['Heading2'])
                elements.append(chart_title)
                elements.append(Spacer(1, 10))
                elements.append(img)
                elements.append(Spacer(1, 20))

            except Exception as e:
                current_app.logger.error(f"Erro ao processar gráfico {chart['name']}: {e}")
                continue

    # Gerar PDF
    doc.build(elements)
    buffer.seek(0)

    # Preparar resposta
    from flask import make_response
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=relatorio_completo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

    return response

def _export_reports_excel(data):
    """Gera Excel do relatório completo."""
    from io import BytesIO
    import pandas as pd

    buffer = BytesIO()

    # Criar workbook com múltiplas abas
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Aba de resumo
        summary_data = {
            'Métrica': ['Total de Alertas', 'Alertas Críticos', 'Sensores Ativos', 'Média de Leituras/Hora'],
            'Valor': ['--', '--', '--', '--'],  # Seria preenchido com dados reais
            'Período': [data.get('filters', {}).get('period', '7d')] * 4
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Resumo', index=False)

        # Outras abas seriam adicionadas com dados específicos

    buffer.seek(0)

    # Preparar resposta
    from flask import make_response
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=relatorio_completo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

    return response
