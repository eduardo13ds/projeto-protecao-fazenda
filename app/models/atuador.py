#app/models/atuador.py
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship
from app.extensions import db


class Atuador(db.Model):
    """
Representa um dispositivo físico que pode executar uma ação (ligar/desligar, abrir/fechar).
    """
    __tablename__ = 'atuadores'
    id_atuador = db.Column('ID_Atuador', db.Integer, primary_key=True)
    nome_atuador = db.Column('Nome_Atuador', db.String(100), nullable=False)
    id_tipo_atuador = db.Column('ID_Tipo_Atuador', db.Integer, ForeignKey('tipos_atuador.ID_Tipo_Atuador'))
    id_fazenda = db.Column('ID_Fazenda', db.Integer, ForeignKey('fazendas.ID_Fazenda'), nullable=False)
    status_atual = db.Column('Status_Atual', db.String(50))
    ultimo_comando_timestamp = db.Column('Ultimo_Comando_Timestamp', db.TIMESTAMP, onupdate=func.current_timestamp())
    parametros_operacao = db.Column('Parametros_Operacao', db.JSON)
    endereco_logico = db.Column('Endereco_Logico', db.String(100))
    fabricante_modelo = db.Column('Fabricante_Modelo', db.String(100))

    fazenda = relationship("Fazenda", back_populates="atuadores")
    tipo_atuador = relationship("TipoAtuador", back_populates="atuadores")
    comandos_registrados = relationship("RegistroComandoAtuador", back_populates="atuador")

