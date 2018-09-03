import os
import tempfile

import pytest

from challenge import app, db

SKU_NOTIFICATIONS = [
    {
        "tipo": "criacao_sku",
        "dataEnvio": "2015-08-18T20:51:22",
        "parametros": {
            "idProduto": 270258,
            "idSku": 322387
        }
    },
    {
        "tipo": "criacao_sku",
        "dataEnvio": "2015-08-18T20:51:22",
        "parametros": {
            "idProduto": 270259,
            "idSku": 322388
        }
    }
]

SKU3 = {
        "nome": "Produto 1",
        "nomeReduzido": None,
        "produtoId": 270229,
        "codigo": "SKU3",
        "modelo": None,
        "ean": None,
        "url": None,
        "foraDeLinha": None,
        "preco": 200.99,
        "precoDe": None,
        "disponivel": True,
        "estoque": 8,
        "dimensoes": {
            "altura": None,
            "largura": None,
            "comprimento": None,
            "peso": None
        },
        "imagens": [],
        "grupos": [],
        "ativo": True
    }

SKU1 = {
        "nome": "Produto 1",
        "nomeReduzido": None,
        "produtoId": 270229,
        "codigo": "SKU1",
        "modelo": None,
        "ean": None,
        "url": None,
        "foraDeLinha": None,
        "preco": 5.99,
        "precoDe": None,
        "disponivel": True,
        "estoque": 8,
        "dimensoes": {
            "altura": None,
            "largura": None,
            "comprimento": None,
            "peso": None
        },
        "imagens": [],
        "grupos": [],
        "ativo": True
    }

SKU2 = {
        "nome": "Produto 1",
        "nomeReduzido": None,
        "produtoId": 270229,
        "codigo": "SKU2",
        "modelo": None,
        "ean": None,
        "url": None,
        "foraDeLinha": None,
        "preco": 11.00,
        "precoDe": None,
        "disponivel": True,
        "estoque": 8,
        "dimensoes": {
            "altura": None,
            "largura": None,
            "comprimento": None,
            "peso": None
        },
        "imagens": [],
        "grupos": [],
        "ativo": True
    }

SKU4 = {
        "nome": "Produto 1",
        "nomeReduzido": None,
        "produtoId": 270229,
        "codigo": "SKU4",
        "modelo": None,
        "ean": None,
        "url": None,
        "foraDeLinha": None,
        "preco": 11.00,
        "precoDe": None,
        "disponivel": True,
        "estoque": 8,
        "dimensoes": {
            "altura": None,
            "largura": None,
            "comprimento": None,
            "peso": None
        },
        "imagens": [],
        "grupos": [],
        "ativo": True
    }

SKU5 = {
        "nome": "Produto 1",
        "nomeReduzido": None,
        "id": 322360,
        "produtoId": 270229,
        "codigo": "SKU5",
        "modelo": None,
        "ean": None,
        "url": None,
        "foraDeLinha": False,
        "preco": 16.99,
        "precoDe": None,
        "disponivel": True,
        "estoque": 8,
        "dimensoes": {
            "altura": None,
            "largura": None,
            "comprimento": None,
            "peso": None
        },
        "imagens": [],
        "grupos": [],
        "ativo": True
}


@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    db.drop_all()
    db.create_all()
    client = app.test_client()
    from challenge.common import create_or_update_sku
    create_or_update_sku(SKU3)
    create_or_update_sku(SKU1)
    create_or_update_sku(SKU2)
    create_or_update_sku(SKU5)

    yield client


def test_base_route(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'Sistema de controle de SKU v1.0' in rv.data


def test_sku_notification(client):
    """Start with a blank database."""
    from challenge.models import Sku
    rv = client.post('/sku/associar', json=SKU_NOTIFICATIONS)
    assert rv.status_code == 200
    assert Sku.query.get(322388).produtoId == 270259


def test_sku_list_preco_min(client):
    """Start with a blank database."""
    rv = client.get('/sku/?preco_min=200')
    assert rv.status_code == 200
    assert SKU3['preco'] == rv.json['records'][0]['preco']


def test_sky_list_preco_max(client):
    rv = client.get('/sku/?preco_max=6')
    assert rv.status_code == 200
    assert SKU1['preco'] == rv.json['records'][0]['preco']


def test_sky_list_preco_max_preco_min(client):
    rv = client.get('/sku/?preco_min=10&preco_max=12')
    assert rv.status_code == 200
    assert SKU2['preco'] == rv.json['records'][0]['preco']


def test_sku_create(client):
    from challenge.models import Sku
    rv = client.post('/sku/', json=SKU4)
    assert rv.status_code == 200
    assert Sku.query.filter(Sku.codigo == 'SKU4').first().codigo == 'SKU4'


def test_sku_invalid(client):
    rv = client.post('/sku/', json=SKU4)
    rv = client.post('/sku/', json=SKU4)
    assert rv.status_code == 400


def test_sku_delete(client):
    from challenge.models import Sku
    assert Sku.query.get(322360).produtoId == 270229
    rv = client.delete('/sku/', json={'id': 322360})
    assert rv.status_code == 200
    assert Sku.query.get(322360) == None
