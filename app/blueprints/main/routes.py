"""
Routes for the main blueprint.
"""
from flask import Blueprint, render_template, jsonify

from app.mqtt.client import mqtt_client

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
def index(area_id=None):
    """Render the home page.

    Args:
        area_id (int, optional): ID da área a ser monitorada. Se não for fornecido,
                                mostra dados de todas as áreas.

    Returns:
        str: Rendered HTML template.
    """
    # Get the latest data and process it
    # Pass area_id to get_latest_data if you want initial data filtered
    # For the template, we'll let JavaScript handle the primary data display
    # but we can pass the current_area_name for the header.

    data = mqtt_client.get_latest_data(area_id) # Get data for initial render if needed for other parts

    current_area_name = None
    if area_id is not None:
        current_area_name = AREA_NAMES.get(area_id, f"Área {area_id}")
    elif data and 'area' in data: # If no area_id in URL, try from initial data
        current_area_name = AREA_NAMES.get(data['area'], f"Área {data['area']}")
    else:
        current_area_name = "Todas" # Default if no area_id and no area in initial data

    # The 'data' passed here is for initial render. JavaScript will fetch frequently.
    # 'current_area' is used by the template, esp. header.
    return render_template('index.html', data=data, current_area=area_id, current_area_name=current_area_name)


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
    # Get the latest data from MQTT client, already filtering by area
    # data = mqtt_client.get_latest_data(area_id)

    data = {
        "adc_value": 3528,
        "area": 1,
        "current_mA": 28.43,
        "humidade": 55.4,
        "probabilidade": 90,
        "razoes": [
            "Umidade baixa: 55.4%",
            "Queda significativa de temperatura: 3.0500000000000007\u00b0C"
        ],
        "temperatura": 22.04,
        "voltage": 2.843076923076923
    }


    # Adicionar um log para depuração
    print(f"Recebido requisição para área {area_id}, retornando dados: {data}")

    return jsonify(data)