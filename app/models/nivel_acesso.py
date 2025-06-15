from app.extensions import db

class NivelAcesso(db.Model):
    """
Define as funções que um usuário pode ter dentro de uma fazenda (ex: Gerente, Operador).
    """
    __tablename__ = 'niveis_acesso'
    id_nivel_acesso = db.Column('ID_Nivel_Acesso', db.Integer, primary_key=True)
    nome_nivel = db.Column('Nome_Nivel', db.String(50), nullable=False, unique=True)
    descricao = db.Column('Descricao', db.Text)
    