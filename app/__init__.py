from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy # Importe SQLAlchemy
from app.config.config import config

# Crie as instâncias fora da função create_app
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # **NOVO: Configuração do Banco de Dados**
    # Usa as informações do seu settings.json
    db_user = "root"
    db_password = "" # Vazio, conforme seu settings.json
    db_host = "localhost"
    db_port = "3306"
    db_name = "sistema_alerta_chuvas"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicialize as extensões com o app
    db.init_app(app)
    login_manager.init_app(app)

    # Importe os modelos AQUI para que eles sejam registrados com o SQLAlchemy
    from app import models

    # Register blueprints
    from app.blueprints.main import main
    from app.blueprints.errors import errors
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app