"""
Routes for the main blueprint.
"""
from flask import Blueprint, render_template, jsonify

from app.mqtt.client import mqtt_client

# Create blueprint
main = Blueprint('main', __name__)


@main.route('/')
@main.route('/<int:area_id>')
def index(area_id=None):
    """Render the home page.

    Args:
        area_id (int, optional): ID da área a ser monitorada. Se não for fornecido,
                                mostra dados de todas as áreas.

    Returns:
        str: Rendered HTML template.
    """
    # Get the latest data and process it
    data = mqtt_client.get_latest_data()

    # Filtrar dados por área se area_id for fornecido
    if area_id is not None and isinstance(data, dict) and 'area' in data:
        if data.get('area') != area_id:
            # Se não houver dados para esta área específica, pode retornar dados vazios
            # ou uma mensagem informando que não há dados para esta área
            data = {}

    return render_template('index.html', data=data, current_area=area_id)


@main.route('/latest-data', methods=['GET'])
@main.route('/latest-data/<int:area_id>', methods=['GET'])
def latest_data_endpoint(area_id=None):
    """Get the latest data from MQTT.

    Args:
        area_id (int, optional): ID da área a ser monitorada. Se não for fornecido,
                                retorna dados de todas as áreas.

    Returns:
        Response: JSON response with the latest data.
    """
    # Get the latest data from MQTT client, já filtrando por área
    data = mqtt_client.get_latest_data(area_id)
    
    # Adicionar um log para depuração
    print(f"Recebido requisição para área {area_id}, retornando dados: {data}")

    return jsonify(data)
