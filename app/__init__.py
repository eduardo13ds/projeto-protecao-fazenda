# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config.config import config
from app.mqtt.client import mqtt_client
from .extensions import db

# --------------------------------------------------------------------
# 1. Instancie as extensões fora da factory
#    Isso permite que outros arquivos (como os modelos) as importem.
# --------------------------------------------------------------------
login_manager = LoginManager()

# Define para qual rota o usuário não logado será redirecionado.
# O formato é 'nome_do_blueprint.nome_da_funcao_da_rota'
# Com base no seu login_route.py, o blueprint se chama 'login'.
login_manager.login_view = 'login.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'


# --------------------------------------------------------------------
# 2. DEFINIÇÃO DO USER_LOADER - A CORREÇÃO PRINCIPAL
#    Esta função deve ser definida aqui, junto com a instância do login_manager.
# --------------------------------------------------------------------
# Importe o modelo de usuário para que o loader possa usá-lo.
from .models.usuario import Usuario

@login_manager.user_loader
def load_user(user_id):
    """
Esta função é o "carregador de usuário". O Flask-Login a usa para
buscar o usuário no banco de dados em cada requisição protegida,
usando o ID que ele guardou na sessão do usuário.
    """
    # db.session.get() é a forma mais eficiente de buscar pela chave primária.
    return db.session.get(Usuario, int(user_id))


# --------------------------------------------------------------------
# 3. A "APPLICATION FACTORY"
#    Esta função constrói e configura a aplicação.
# --------------------------------------------------------------------
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configuração do Banco de Dados
    db_user = "root"
    db_password = ""
    db_host = "localhost"
    db_port = "3306"
    db_name = "stormguard"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicialize as extensões, conectando-as à instância da aplicação
    db.init_app(app)
    login_manager.init_app(app)
    mqtt_client.init_app(app)

    with app.app_context():
        from .ml_services import PredictionService
        try:
            PredictionService.get_model()
        except Exception as e:
            app.logger.critical(f"Falha CRÍTICA ao carregar o modelo de ML na inicialização: {e}")

    # Registro dos Blueprints
    from .blueprints.main import main as main_blueprint
    from .blueprints.errors import errors as errors_blueprint
    from .blueprints.login import login_register as login_blueprint
    from .blueprints.db_interaction import admin_bp as admin_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(errors_blueprint)
    app.register_blueprint(login_blueprint)
    app.register_blueprint(admin_blueprint)

    return app

