# app/models/usuario.py

from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

# Herde de db.Model e UserMixin
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    # Suas colunas existentes
    id_usuario = db.Column('ID_Usuario', db.Integer, primary_key=True)
    nome_usuario = db.Column('Nome_Usuario', db.String(50), nullable=False, unique=True)
    senha_hash = db.Column('Senha_Hash', db.String(255), nullable=False)
    nome_completo = db.Column('Nome_Completo', db.String(100))
    email = db.Column('Email', db.String(100), nullable=False, unique=True)
    status_conta = db.Column('Status_Conta', db.Enum('Ativa', 'Inativa', 'Bloqueada'), default='Ativa')
    data_criacao = db.Column('Data_Criacao', db.TIMESTAMP, server_default=db.func.current_timestamp())
    ultimo_login = db.Column('Ultimo_Login', db.TIMESTAMP)

    # Relacionamento Muitos-para-Muitos com Fazendas
    fazendas = relationship(
        "Fazenda",
        secondary='usuario_fazenda_acesso',
        back_populates="usuarios"
    )

    # ==========================================================
    # CORREÇÃO: RELAÇÕES DE RETORNO QUE FALTAVAM
    # ==========================================================
    # Esta é a "outra mão" da relação com o modelo Alerta.
    alertas_reconhecidos = relationship("Alerta", back_populates="usuario_reconheceu")

    # Esta é a "outra mão" da relação com o modelo RegistroComandoAtuador.
    comandos_executados = relationship("RegistroComandoAtuador", back_populates="usuario_executor")
    # ==========================================================


    # --- MÉTODOS NECESSÁRIOS PARA O FLASK-LOGIN ---

    def get_id(self):
        """Retorna o ID do usuário (deve ser string)."""
        return str(self.id_usuario)

    def set_password(self, password):
        """Cria um hash da senha e o armazena."""
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return check_password_hash(self.senha_hash, password)

