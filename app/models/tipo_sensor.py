from sqlalchemy.orm import relationship

from app.extensions import db


class TipoSensor(db.Model):
    """
Tabela de tipos de sensores (ex: Temperatura, Umidade, Pressão).
    """
    __tablename__ = 'tipos_sensor'
    id_tipo_sensor = db.Column('ID_Tipo_Sensor', db.Integer, primary_key=True)
    nome_tipo = db.Column('Nome_Tipo', db.String(50), nullable=False)
    unidade_medida = db.Column('Unidade_Medida', db.String(20))
    sensores = relationship("Sensor", back_populates="tipo_sensor")
