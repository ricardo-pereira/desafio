from challenge import db
from sqlalchemy.orm import validates


class Sku(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produtoId = db.Column(db.Integer)
    nome = db.Column(db.String(120))
    nomeReduzido = db.Column(db.String(80))
    codigo = db.Column(db.String(80), unique=True, nullable=False)
    modelo = db.Column(db.String(80))
    ean = db.Column(db.String(80))
    url = db.Column(db.String(80))
    foraDeLinha = db.Column(db.Boolean)
    preco = db.Column(db.Float)
    precoDe = db.Column(db.Float)
    disponivel = db.Column(db.Boolean)
    estoque = db.Column(db.Integer)
    dimensoes = db.String(256)
    imagens = db.Column(db.String(256), default='[]')
    grupos = db.Column(db.String(256), default='[]')
    ativo = db.Column(db.Boolean)

    @validates('imagens', 'grupos')
    def validate_lists(self, key, value):
        if not isinstance(value, str):
            value = str(value)

    def __repr__(self):
        return '<Sku %r>' % self.id
