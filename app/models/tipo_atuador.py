from sqlalchemy.orm import relationship

from app.extensions import db


class TipoAtuador(db.Model):
    """
Tabela de tipos de atuadores (ex: Controle de Estufa, Portão Eletrônico).
    """
    __tablename__ = 'tipos_atuador'
    id_tipo_atuador = db.Column('ID_Tipo_Atuador', db.Integer, primary_key=True)
    nome_tipo = db.Column('Nome_Tipo', db.String(50), nullable=False)
    atuadores = relationship("Atuador", back_populates="tipo_atuador")

