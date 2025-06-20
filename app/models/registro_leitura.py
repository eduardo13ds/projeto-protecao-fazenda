from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship
from app.extensions import db


class RegistroLeitura(db.Model):
    """
    Armazena o histórico de todas as leituras de dados recebidas dos sensores.
    Cada registro está vinculado a um sensor específico.
    """
    __tablename__ = 'registro_leituras'

    id_leitura = db.Column('ID_Leitura', db.BigInteger, primary_key=True)
    id_sensor = db.Column('ID_Sensor', db.Integer, ForeignKey('sensores.ID_Sensor'), nullable=False)
    valor_leitura = db.Column('Valor_Leitura', db.String(255), nullable=False)
    timestamp_leitura = db.Column('Timestamp_Leitura', db.TIMESTAMP, server_default=func.current_timestamp())
    qualidade = db.Column('Qualidade', db.Enum('Confiavel', 'Ruido', 'Fora da Faixa'), default='Confiavel')

    # Campos adicionais para melhor rastreabilidade
    valor_numerico = db.Column('Valor_Numerico', db.DECIMAL(15, 6), nullable=True)  # Valor convertido para cálculos
    unidade_medida = db.Column('Unidade_Medida', db.String(20), nullable=True)  # Cópia da unidade do tipo de sensor
    observacoes = db.Column('Observacoes', db.Text, nullable=True)

    # Relacionamentos
    sensor = relationship("Sensor", back_populates="leituras")

    def __repr__(self):
        return f'<RegistroLeitura ID={self.id_leitura} Sensor={self.id_sensor} Valor={self.valor_leitura} Time={self.timestamp_leitura}>'

    @property
    def dispositivo(self):
        """Acessa o dispositivo através do sensor"""
        return self.sensor.dispositivo if self.sensor else None

    @property
    def fazenda(self):
        """Acessa a fazenda através do sensor e dispositivo"""
        return self.sensor.fazenda if self.sensor else None

    @property
    def tipo_sensor(self):
        """Acessa o tipo de sensor através do sensor"""
        return self.sensor.tipo_sensor if self.sensor else None

    def converter_valor_numerico(self):
        """Converte o valor_leitura string para um valor numérico"""
        try:
            # Remove vírgulas e converte para float
            valor_limpo = str(self.valor_leitura).replace(',', '.')
            self.valor_numerico = float(valor_limpo)
            return True
        except (ValueError, TypeError):
            self.valor_numerico = None
            return False

    def validar_qualidade(self, limite_min=None, limite_max=None):
        """Valida a qualidade da leitura baseada nos limites do sensor"""
        if not self.valor_numerico:
            if not self.converter_valor_numerico():
                self.qualidade = 'Ruido'
                return False

        # Usa os limites do sensor se não fornecidos
        if limite_min is None and self.sensor:
            limite_min = self.sensor.limite_minimo_alerta
        if limite_max is None and self.sensor:
            limite_max = self.sensor.limite_maximo_alerta

        # Verifica se está dentro da faixa
        if limite_min is not None and self.valor_numerico < limite_min:
            self.qualidade = 'Fora da Faixa'
            return False
        if limite_max is not None and self.valor_numerico > limite_max:
            self.qualidade = 'Fora da Faixa'
            return False

        self.qualidade = 'Confiavel'
        return True

    @classmethod
    def obter_ultimas_leituras(cls, sensor_id, limite=10):
        """Obtém as últimas N leituras de um sensor específico"""
        return cls.query.filter_by(id_sensor=sensor_id)\
                       .order_by(cls.timestamp_leitura.desc())\
                       .limit(limite).all()

    @classmethod
    def obter_leituras_por_periodo(cls, sensor_id, data_inicio, data_fim):
        """Obtém leituras de um sensor em um período específico"""
        return cls.query.filter_by(id_sensor=sensor_id)\
                       .filter(cls.timestamp_leitura >= data_inicio)\
                       .filter(cls.timestamp_leitura <= data_fim)\
                       .order_by(cls.timestamp_leitura.asc()).all()

    @classmethod
    def obter_media_por_dispositivo(cls, dispositivo_id, horas=24):
        """Obtém a média das leituras de todos os sensores de um dispositivo nas últimas N horas"""
        from sqlalchemy import and_, func as sql_func
        from datetime import datetime, timedelta

        data_limite = datetime.utcnow() - timedelta(hours=horas)

        return db.session.query(
            cls.id_sensor,
            sql_func.avg(cls.valor_numerico).label('media'),
            sql_func.count(cls.id_leitura).label('total_leituras')
        ).join(
            cls.sensor
        ).filter(
            and_(
                cls.sensor.has(id_dispositivo=dispositivo_id),
                cls.timestamp_leitura >= data_limite,
                cls.valor_numerico.isnot(None)
            )
        ).group_by(cls.id_sensor).all()
