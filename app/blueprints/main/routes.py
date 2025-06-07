"""
Routes for the main blueprint.
"""
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm # Importe o formulário
from app.models import Usuario # Importe o modelo de usuário
from app import db # Importe a instância do db
from werkzeug.security import check_password_hash # Para checar a senha
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.mqtt.client import mqtt_client
from app.forms import LoginForm # Importe o formulário
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
@login_required

def latest_data_endpoint(area_id=None):
    """Get the latest data from MQTT.

    Args:
        area_id (int, optional): ID da área a ser monitorada.
                                Se não for fornecido, retorna uma lista de todos os alertas ativos.

    Returns:
        Response: JSON response with the latest data for a specific area
                  or a list of active alerts.
    """
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
@login_required

def latest_inmet_endpoint():
    """Retorna o último dado recebido do INMET via MQTT."""
    data = mqtt_client.get_latest_inmet_data()
    return jsonify(data)

# Rota de Login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # **LÓGICA REAL AQUI**
        # 1. Busque o usuário no banco de dados pelo nome de usuário do formulário
        user = Usuario.query.filter_by(Nome_Usuario=form.username.data).first()

        # 2. Verifique se o usuário existe e se a senha está correta
        if user is None or not user.check_password(form.password.data):
            flash('Nome de usuário ou senha inválidos', 'danger')
            return redirect(url_for('main.login'))

        # 3. Se tudo estiver correto, faça o login do usuário
        login_user(user, remember=form.remember_me.data)
        flash('Login realizado com sucesso!', 'success')

        # Redireciona para a página que o usuário tentou acessar ou para o index
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.index'))

    return render_template('login.html', title='Login', form=form)

# Rota de Logout
@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# Adicione outras rotas aqui (registro, etc.)