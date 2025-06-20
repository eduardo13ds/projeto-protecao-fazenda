from sqlalchemy.orm import relationship
from app.extensions import db


class TipoSensor(db.Model):
    """
    Tabela de tipos de sensores (ex: Temperatura, Umidade, Pressão).
    """
    __tablename__ = 'tipos_sensor'
    id_tipo_sensor = db.Column('ID_Tipo_Sensor', db.Integer, primary_key=True)
    nome_tipo = db.Column('Nome_Tipo', db.String(50), nullable=False, unique=True)
    unidade_medida = db.Column('Unidade_Medida', db.String(20))
    descricao = db.Column('Descricao', db.Text, nullable=True)

    # Relacionamento com sensores
    sensores = relationship("Sensor", back_populates="tipo_sensor", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<TipoSensor {self.nome_tipo} ({self.unidade_medida})>'

    @property
    def sensores_ativos(self):
        """Retorna apenas sensores ativos deste tipo"""
        return self.sensores.filter_by(status='Ativo')

    @property
    def total_sensores(self):
        """Retorna o número total de sensores deste tipo"""
        return self.sensores.count()
