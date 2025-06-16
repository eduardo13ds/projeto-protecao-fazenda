# app/models/documento_verificacao.py
from app.extensions import db
from sqlalchemy import func

class DocumentoVerificacao(db.Model):
    __tablename__ = 'documentos_verificados'
    id = db.Column(db.String(36), primary_key=True) # UUID
    tabela_origem = db.Column(db.String(100), nullable=False)
    hash_conteudo = db.Column(db.String(64), nullable=False, unique=True) # SHA-256
    data_emissao = db.Column(db.TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    id_usuario_emissor = db.Column(db.Integer, db.ForeignKey('usuarios.ID_Usuario'))

    usuario_emissor = db.relationship("Usuario")