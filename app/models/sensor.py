#app/models/sensor.py
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db

class Sensor(db.Model):
    """
    Representa um sensor físico associado a um dispositivo.
    Cada sensor tem um tipo específico (temperatura, umidade, etc.)
    """
    __tablename__ = 'sensores'

    id_sensor = db.Column('ID_Sensor', db.Integer, primary_key=True)
    id_tipo_sensor = db.Column('ID_Tipo_Sensor', db.Integer, db.ForeignKey('tipos_sensor.ID_Tipo_Sensor'), nullable=False)
    id_dispositivo = db.Column('ID_Dispositivo', db.Integer, db.ForeignKey('dispositivos.ID_Dispositivo'), nullable=False)

    # Campos opcionais para configuração do sensor
    status = db.Column('Status', db.Enum('Ativo', 'Inativo', 'Manutencao'), default='Ativo')
    ultima_leitura = db.Column('Ultima_Leitura', db.TIMESTAMP, nullable=True)
    limite_minimo_alerta = db.Column('Limite_Minimo_Alerta', db.DECIMAL(10, 4), nullable=True)
    limite_maximo_alerta = db.Column('Limite_Maximo_Alerta', db.DECIMAL(10, 4), nullable=True)

    # Relacionamentos
    tipo_sensor = relationship("TipoSensor", back_populates="sensores")
    # dispositivo é definido automaticamente pelo backref no modelo Dispositivo
    leituras = relationship("RegistroLeitura", back_populates="sensor", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Sensor ID={self.id_sensor} Tipo={self.tipo_sensor.nome_tipo if self.tipo_sensor else "N/A"} Dispositivo={self.id_dispositivo}>'

    @property
    def fazenda(self):
        """Propriedade para acessar a fazenda através do dispositivo"""
        return self.dispositivo.fazenda if self.dispositivo else None

    @property
    def nome_completo(self):
        """Nome amigável do sensor incluindo tipo e dispositivo"""
        if self.tipo_sensor and self.dispositivo:
            return f"{self.tipo_sensor.nome_tipo} - {self.dispositivo.nome_amigavel}"
        return f"Sensor ID {self.id_sensor}"
