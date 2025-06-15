from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship

from app.extensions import db


class Sensor(db.Model):
    """
Representa um dispositivo sensor físico instalado em uma fazenda.
    """
    __tablename__ = 'sensores'
    id_sensor = db.Column('ID_Sensor', db.Integer, primary_key=True)
    nome_sensor = db.Column('Nome_Sensor', db.String(100), nullable=False)
    id_tipo_sensor = db.Column('ID_Tipo_Sensor', db.Integer, ForeignKey('tipos_sensor.ID_Tipo_Sensor'))
    id_fazenda = db.Column('ID_Fazenda', db.Integer, ForeignKey('fazendas.ID_Fazenda'), nullable=False)
    status = db.Column('Status', db.Enum('Ativo', 'Inativo', 'Offline', 'Manutencao'), default='Ativo')
    ultima_leitura = db.Column('Ultima_Leitura', db.TIMESTAMP, onupdate=func.current_timestamp())
    limite_minimo_alerta = db.Column('Limite_Minimo_Alerta', db.DECIMAL(10, 2))
    limite_maximo_alerta = db.Column('Limite_Maximo_Alerta', db.DECIMAL(10, 2))
    endereco_logico = db.Column('Endereco_Logico', db.String(100))
    fabricante_modelo = db.Column('Fabricante_Modelo', db.String(100))

    fazenda = relationship("Fazenda", back_populates="sensores")
    tipo_sensor = relationship("TipoSensor", back_populates="sensores")
    leituras = relationship("RegistroLeitura", back_populates="sensor", cascade="all, delete-orphan")

