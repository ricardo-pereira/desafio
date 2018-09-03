import json
import requests
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import sandbox

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{0}{1}.db'.format(sandbox['database']['path'], sandbox['database']['filename'])
db = SQLAlchemy(app)

from challenge.models import Sku
from challenge.common import serialize_json, create_or_update_sku

# inicializacao dos bancos definidos no modelo de dados
db.create_all()


# rota base
@app.route('/')
def base_route():
    return 'Sistema de controle de SKU v1.0'


# insert ou update de registro de sku
@app.route('/sku', methods=['POST'])
@app.route('/sku/', methods=['POST'])
def sku_create_or_update():
    try:
        data = json.loads(request.data)
        # checagem basica de integradade pra insercao ou update
        create_or_update_sku(data)
    except Exception as e:
        # Erro generico
        app.logger.error('Erro no insert ou update para SKU %r' % e)
        return jsonify('{status: error, descricao: %s}' % e), 400

    return jsonify('{status: ok}')


# remocao de sku da base local
@app.route('/sku', methods=['DELETE'])
@app.route('/sku/', methods=['DELETE'])
def sku_delete():
    try:
        data = json.loads(request.data)
        integrity_check = Sku.query.get(data['id'])
        # verificar existencia antes de efetuar delete
        if integrity_check:
            db.session.delete(integrity_check)
            db.session.commit()
        else:
            # validacao basica de existencia falhou
            app.logger.error('Erro deletando SKU, id invalido %r' % data.get('id'))
            return jsonify('{status: error, descricao: Not a valid id to be deleted}'), 400
    except Exception as e:
        # Erro generico
        app.logger.error('Erro deletando SKU %r' % e)
        return jsonify('{status: error, descricao: %s}' % e), 400

    return jsonify('{status: ok}')


@app.route('/sku', methods=['GET'])
@app.route('/sku/', methods=['GET'])
def sku_list():
    # parametros para busca de acordo com o preco da SKU (opcionais)
    preco_min = request.args.get('preco_min')
    preco_max = request.args.get('preco_max')
    # verificacao dos parametros passados
    if preco_min is None and preco_max:
        skus_list = Sku.query.filter(Sku.preco <= float(preco_max)).order_by(Sku.preco.asc()).all()
    elif preco_max is None and preco_min:
        skus_list = Sku.query.filter(Sku.preco >= float(preco_min)).order_by(Sku.preco.asc()).all()
    elif preco_min and preco_max:
        skus_list = Sku.query.filter(Sku.preco >= float(preco_min), Sku.preco <= float(preco_max)).order_by(Sku.preco.asc()).all()
    else:
        skus_list = Sku.query.order_by(Sku.preco.asc()).all()
    # metodo que faz parse da lista retornada pela query para json    
    resp = serialize_json(skus_list)

    return jsonify(records=resp)


@app.route('/sku/associar', methods=['POST'])
def sku_association():
	# parse da notificacao
    json_data = json.loads(request.data)

    for notification in json_data:
        parametros = notification.get('parametros')
        # checagem dos parametros minimos
        if parametros:
            id_sku = parametros.get('idSku')
            id_produto = parametros.get('idProduto')

            if id_sku and id_produto:
            	# chamada a api de marketplace para recebimento dos dados do SKU
                sku_data = requests.get('{0}{1}'.format(sandbox['url'], sandbox['views']['GET_SKU_DATA'].format(id_produto, id_sku)), headers={'Authorization': 'Basic {0}'.format(sandbox['api_key'])})
                # insercao ou update na base local
                create_or_update_sku(sku_data.json())

    return jsonify(records_processed=json_data)
