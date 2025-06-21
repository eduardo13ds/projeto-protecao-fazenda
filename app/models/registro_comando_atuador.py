#app/models/registro_comando_atuador.py
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship

from app.extensions import db


class RegistroComandoAtuador(db.Model):
    """
Armazena o histórico de todos os comandos enviados aos atuadores e seu status.
    """
    __tablename__ = 'registro_comandos_atuadores'
    id_registro_comando = db.Column('ID_Registro_Comando', db.BigInteger, primary_key=True)
    id_atuador = db.Column('ID_Atuador', db.Integer, ForeignKey('atuadores.ID_Atuador'), nullable=True)
    id_usuario_executor = db.Column('ID_Usuario_Executor', db.Integer, ForeignKey('usuarios.ID_Usuario'))
    comando_executado = db.Column('Comando_Executado', db.String(100))
    parametros_comando = db.Column('Parametros_Comando', db.JSON)
    timestamp_comando = db.Column('Timestamp_Comando', db.TIMESTAMP, server_default=func.current_timestamp())
    status_execucao = db.Column('Status_Execucao', db.Enum('Sucesso', 'Falha', 'Pendente'), default='Pendente')
    mensagem_retorno = db.Column('Mensagem_Retorno', db.Text)

    atuador = relationship("Atuador", back_populates="comandos_registrados")
    usuario_executor = relationship("Usuario", back_populates="comandos_executados")
