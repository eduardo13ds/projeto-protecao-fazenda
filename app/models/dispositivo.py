# app/models/dispositivo.py
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db

class Dispositivo(db.Model):
    """
    Representa um dispositivo físico (ex: um ESP32) instalado no campo.
    Cada dispositivo pode ter múltiplos sensores associados.
    """
    __tablename__ = 'dispositivos'

    id_dispositivo = db.Column('ID_Dispositivo', db.Integer, primary_key=True)

    # Este é o ID único que o dispositivo enviará via MQTT. Ex: 'sensor_area_norte_01'
    identificador_unico = db.Column('Identificador_Unico', db.String(80), unique=True, nullable=False, index=True)

    nome_amigavel = db.Column('Nome_Amigavel', db.String(100), nullable=True)
    area = db.Column('Area', db.String(50), nullable=True)
    id_fazenda = db.Column('ID_Fazenda', db.Integer, ForeignKey('fazendas.ID_Fazenda'), nullable=False)

    # Campos adicionais para melhor gerenciamento
    status = db.Column('Status', db.Enum('Ativo', 'Inativo', 'Manutencao'), default='Ativo')
    data_instalacao = db.Column('Data_Instalacao', db.TIMESTAMP, server_default=db.func.current_timestamp())
    ultimo_ping = db.Column('Ultimo_Ping', db.TIMESTAMP, nullable=True)
    versao_firmware = db.Column('Versao_Firmware', db.String(20), nullable=True)
    observacoes = db.Column('Observacoes', db.Text, nullable=True)

    # Relacionamentos
    fazenda = relationship("Fazenda", back_populates="dispositivos")
    sensores = relationship('Sensor', backref='dispositivo', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Dispositivo {self.identificador_unico} - {self.nome_amigavel}>'

    @property
    def sensores_ativos(self):
        """Retorna apenas sensores ativos deste dispositivo"""
        return self.sensores.filter_by(status='Ativo')

    @property
    def total_sensores(self):
        """Retorna o número total de sensores deste dispositivo"""
        return self.sensores.count()

    @property
    def tipos_sensores_disponiveis(self):
        """Retorna os tipos de sensores que ainda não estão associados a este dispositivo"""
        from app.models.tipo_sensor import TipoSensor
        sensores_associados_ids = [s.id_tipo_sensor for s in self.sensores]
        return TipoSensor.query.filter(~TipoSensor.id_tipo_sensor.in_(sensores_associados_ids)).all()

    @property
    def esta_online(self):
        """Verifica se o dispositivo está online baseado no último ping"""
        if not self.ultimo_ping:
            return False
        from datetime import datetime, timedelta
        return self.ultimo_ping > datetime.utcnow() - timedelta(minutes=5)

    def pode_receber_sensor(self, tipo_sensor_id):
        """Verifica se o dispositivo pode receber um sensor do tipo especificado"""
        return not self.sensores.filter_by(id_tipo_sensor=tipo_sensor_id).first()

    def associar_sensor(self, tipo_sensor_id):
        """Associa um novo sensor a este dispositivo"""
        if self.pode_receber_sensor(tipo_sensor_id):
            from app.models.sensor import Sensor
            novo_sensor = Sensor(
                id_dispositivo=self.id_dispositivo,
                id_tipo_sensor=tipo_sensor_id
            )
            db.session.add(novo_sensor)
            return novo_sensor
        return None

    def desassociar_sensor(self, sensor_id):
        """Remove um sensor deste dispositivo"""
        sensor = self.sensores.filter_by(id_sensor=sensor_id).first()
        if sensor:
            # Verifica se há leituras associadas
            if sensor.leituras.count() > 0:
                return False, "Sensor possui registros de leitura e não pode ser removido"
            db.session.delete(sensor)
            return True, "Sensor removido com sucesso"
        return False, "Sensor não encontrado"
