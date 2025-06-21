#app/models/tabelas_associacao.py
from app.extensions import db

usuario_fazenda_acesso = db.Table(
    "usuario_fazenda_acesso",
    db.Column(
        "ID_Usuario", db.Integer, db.ForeignKey("usuarios.ID_Usuario"), primary_key=True
    ),
    db.Column(
        "ID_Fazenda", db.Integer, db.ForeignKey("fazendas.ID_Fazenda"), primary_key=True
    ),
    db.Column(
        "ID_Nivel_Acesso",
        db.Integer,
        db.ForeignKey("niveis_acesso.ID_Nivel_Acesso"),
        nullable=False,
    ),
)

# Tabela de associação para o relacionamento muitos-para-muitos entre Área e Sensor
# Define uma tabela simples sem um modelo de classe, contendo apenas as chaves estrangeiras.
area_sensor_association = db.Table(
    "area_sensor",
    db.Column("id_area", db.Integer, db.ForeignKey("areas.id_area"), primary_key=True),
    db.Column(
        "id_sensor", db.Integer, db.ForeignKey("sensores.id_sensor"), primary_key=True
    ),
)

# Tabela de associação para o relacionamento muitos-para-muitos entre Área e Atuador
area_atuador_association = db.Table(
    "area_atuador",
    db.Column("id_area", db.Integer, db.ForeignKey("areas.id_area"), primary_key=True),
    db.Column(
        "id_atuador",
        db.Integer,
        db.ForeignKey("atuadores.id_atuador"),
        primary_key=True,
    ),
)
