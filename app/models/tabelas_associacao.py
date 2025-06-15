from app.extensions import db

usuario_fazenda_acesso = db.Table('usuario_fazenda_acesso',
                                  db.Column('ID_Usuario', db.Integer, db.ForeignKey('usuarios.ID_Usuario'), primary_key=True),
                                  db.Column('ID_Fazenda', db.Integer, db.ForeignKey('fazendas.ID_Fazenda'), primary_key=True),
                                  db.Column('ID_Nivel_Acesso', db.Integer, db.ForeignKey('niveis_acesso.ID_Nivel_Acesso'), nullable=False)
                                  )