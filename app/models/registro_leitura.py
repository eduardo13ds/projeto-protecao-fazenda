from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship

from app.extensions import db


class RegistroLeitura(db.Model):
    """
Armazena o histórico de todas as leituras de dados recebidas dos sensores.
    """
    __tablename__ = 'registro_leituras'
    id_leitura = db.Column('ID_Leitura', db.BigInteger, primary_key=True)
    id_sensor = db.Column('ID_Sensor', db.Integer, ForeignKey('sensores.ID_Sensor'), nullable=False)
    valor_leitura = db.Column('Valor_Leitura', db.String(255), nullable=False)
    timestamp_leitura = db.Column('Timestamp_Leitura', db.TIMESTAMP, server_default=func.current_timestamp())
    qualidade = db.Column('Qualidade', db.Enum('Confiavel', 'Ruido', 'Fora da Faixa'), default='Confiavel')

    sensor = relationship("Sensor", back_populates="leituras")
