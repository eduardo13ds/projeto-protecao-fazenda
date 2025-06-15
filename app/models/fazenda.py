from app.extensions import db
from sqlalchemy.orm import relationship
from app.models.tabelas_associacao import usuario_fazenda_acesso

class Fazenda(db.Model):
    """
Cadastra as propriedades rurais (tenants) que são monitoradas pelo sistema.
    """
    __tablename__ = 'fazendas'
    id_fazenda = db.Column('ID_Fazenda', db.Integer, primary_key=True)
    nome_fazenda = db.Column('Nome_Fazenda', db.String(100), nullable=False)
    localizacao_latitude = db.Column('Localizacao_Latitude', db.DECIMAL(10, 8))
    localizacao_longitude = db.Column('Localizacao_Longitude', db.DECIMAL(11, 8))
    area_total_hectares = db.Column('Area_Total_Hectares', db.DECIMAL(10, 2))
    descricao = db.Column('Descricao', db.Text)

    # Relacionamento Muitos-para-Muitos com Usuários
    usuarios = relationship(
        "Usuario",
        secondary=usuario_fazenda_acesso,
        back_populates="fazendas"
    )

    # Relacionamentos Um-para-Muitos (o "Um" está aqui)
    # cascade="all, delete-orphan": se uma fazenda for deletada, seus sensores,
    # atuadores e alertas associados também serão.
    sensores = relationship("Sensor", back_populates="fazenda", cascade="all, delete-orphan")
    atuadores = relationship("Atuador", back_populates="fazenda", cascade="all, delete-orphan")
    alertas = relationship("Alerta", back_populates="fazenda", cascade="all, delete-orphan")
