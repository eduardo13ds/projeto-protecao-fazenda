from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# Supondo que você configurará o SQLAlchemy no seu app
from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

# Você precisará de uma instância do SQLAlchemy.
# Por simplicidade, vamos definir a estrutura aqui.
# Em um projeto real, a 'db' viria de um arquivo central.
# from app import db

Base = declarative_base()

class Usuario(UserMixin, Base):
    __tablename__ = 'Usuarios'

    ID_Usuario = Column(Integer, primary_key=True)
    Nome_Usuario = Column(String(50), unique=True, nullable=False)
    Email = Column(String(100), unique=True, nullable=False)
    Senha_Hash = Column(String(255), nullable=False)

    def get_id(self):
        return str(self.ID_Usuario)

    def set_password(self, password):
        self.Senha_Hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Senha_Hash, password)

# Fora da classe, no seu __init__.py ou models.py, defina o user_loader
from app import login_manager

# Esta função é usada pelo Flask-Login para recarregar o objeto do usuário
# a partir do ID do usuário armazenado na sessão.
@login_manager.user_loader
def load_user(user_id):
    # Aqui você deve consultar seu banco de dados para obter o usuário pelo ID.
    # Exemplo com SQLAlchemy: return db.session.get(Usuario, int(user_id))
    # Por enquanto, é um placeholder.
    return None # Substitua pela sua lógica de banco de dados