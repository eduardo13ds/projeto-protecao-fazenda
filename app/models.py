# em app/models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager # Importe o 'db' do __init__.py

class Usuario(UserMixin, db.Model): # Mude Base para db.Model
    __tablename__ = 'Usuarios'

    ID_Usuario = db.Column(db.Integer, primary_key=True)
    Nome_Usuario = db.Column(db.String(50), unique=True, nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Senha_Hash = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.ID_Usuario)

    def set_password(self, password):
        self.Senha_Hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Senha_Hash, password)

@login_manager.user_loader
def load_user(user_id):
    # Agora podemos fazer a consulta real
    return db.session.get(Usuario, int(user_id))