"""
Application factory module.
"""
from flask import Flask

from app.config.config import config
from app.mqtt.client import mqtt_client


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

    # Register blueprints
    from app.blueprints.main import main
    from app.blueprints.errors import errors

    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
