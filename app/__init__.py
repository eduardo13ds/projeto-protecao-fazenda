"""
Application factory module.
"""
from flask import Flask
from flask_login import LoginManager # Importe o LoginManager

from app.config.config import config
from app.mqtt.client import mqtt_client

# Crie a instância do gerenciador de login
login_manager = LoginManager()
# Defina a view de login. Se um usuário não logado tentar acessar uma página protegida,
# ele será redirecionado para esta rota.
login_manager.login_view = 'main.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    """Create and configure the Flask application.

    Args:
        config_name (str): The configuration to use. Default is 'default'.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize MQTT client
    mqtt_client.init_app(app)

    # Inicialize o LoginManager com o app
    login_manager.init_app(app)

    # Register blueprints
    from app.blueprints.main import main
    from app.blueprints.errors import errors

    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app