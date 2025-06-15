from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship

from app.extensions import db


class Alerta(db.Model):
    """
Registra os alertas gerados pelo sistema com base nas leituras dos sensores.
    """
    __tablename__ = 'alertas'
    id_alerta = db.Column('ID_Alerta', db.Integer, primary_key=True)
    id_fazenda = db.Column('ID_Fazenda', db.Integer, ForeignKey('fazendas.ID_Fazenda'), nullable=False)
    timestamp_emissao = db.Column('Timestamp_Emissao', db.TIMESTAMP, server_default=func.current_timestamp())
    tipo_alerta = db.Column('Tipo_Alerta', db.String(100))
    intensidade = db.Column('Intensidade', db.Enum('Leve', 'Moderado', 'Severo', 'Critico'))
    probabilidade = db.Column('Probabilidade', db.DECIMAL(5, 2))
    mensagem = db.Column('Mensagem', db.Text)
    status = db.Column('Status', db.Enum('Ativo', 'Reconhecido', 'Resolvido'), default='Ativo')
    timestamp_reconhecimento = db.Column('Timestamp_Reconhecimento', db.TIMESTAMP, nullable=True)
    id_usuario_reconheceu = db.Column('ID_Usuario_Reconheceu', db.Integer, ForeignKey('usuarios.ID_Usuario'))

    fazenda = relationship("Fazenda", back_populates="alertas")
    usuario_reconheceu = relationship("Usuario", back_populates="alertas_reconhecidos")
