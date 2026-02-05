from flask import Blueprint, jsonify, request, current_app
from app.models.user import LoginPayload
#valicao de erro
from pydantic import ValidationError

from app import db
from bson import ObjectId
from app.models.products import *
from app.decorators import token_required
from datetime import datetime, timedelta, timezone
import jwt


# Define the Blueprint for main routes, ja o name vai definir o nome do blueprint
main_bp = Blueprint('main', __name__)

# Define a simple route within this blueprint

#RF: O nosso sisttema deve permitir que um usuario se autentique para obter um token
#isso aqui é a rota de login
@main_bp.route('/login', methods=['POST'])
def login():
    #costumicao de mensagem
    try:
        raw_data = request.get_json()
        user_data=LoginPayload(**raw_data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return jsonify({"error":"Erro durante a requisicao do dados de login."}), 500
    
    if user_data.username == "admin" and user_data.password == "password":
        #ele ja espera um dicionario, entao a gente tem que passar um dicionario com as informacoes do usuario, e o segredo para assinar o token, e o algoritmo de assinatura
        token=jwt.encode(
            {
                "user_id": user_data.username,
                "exp": datetime.now(timezone.utc)+timedelta(minutes=30)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return jsonify({'acess_token': token}),200
    else:
        return jsonify({"message": "Credenciais inválidas."}), 401
#o model dump json e para converter o modelo pydantic em json


#RF: O sistema deve permitir listagem de todos os produtos
@main_bp.route('/products', methods=['GET'])
def get_products():
    products_cursor=db.products.find({})
    products_list=[ProductDBMondel(**product).model_dump(by_alias=True, exclude_none=True) for product in products_cursor]
    return jsonify(products_list)

#RF: O sistema deve permitir a criacao de um novo produto
@token_required
@main_bp.route('/products', methods=['POST'])
def create_product(token):
    try:
        product = Produt(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()})
    result = db.products.insert_one(product.model_dump())

    return jsonify({"message": "Produto criado com sucesso.",
                     "product_id": str(result.inserted_id)}),201

#RF: O sistema deve permitir a visualizacao dos detalhes de um unico produto
@main_bp.route('/products/<string:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    try:
        oid =ObjectId(product_id)
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar os detalhes do produto, erro: {e}"})
    product = db.products.find_one({"_id": oid})
    
    if product:
        product_model=ProductDBMondel(**product).model_dump(by_alias=True, exclude_none=True)
        return jsonify(product_model)
    else:
        return jsonify({"error": "Produto não encontrado"}), 404


#RF: O sistema deve permitir a atualizacao de um unico produto
@main_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    return jsonify({"message": f"Esta é a rota de atualização do produto com ID {product_id}."})

#RF: O sistema deve permitir a delecao de um unico produto e produto existente
@main_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    return jsonify({"message": f"Esta é a rota de deleção do produto com ID {product_id}."})

#RF: o sistema deve permitir a importacao de vendas atrave de um arquivo
@main_bp.route('/sales/upload', methods=['POST'])
def upload_sales():
    return jsonify({"message": "Esta é a rota de upload de vendas."})

@main_bp.route('/')
def index():
    return jsonify({"message": "Bem vindo ao Stylesync!"})



#escreve cada necessaridade de rota aqui dentro do blueprint main_bp
#com metico post
