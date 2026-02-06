from flask import Blueprint, jsonify, request, current_app
from app.models.user import LoginPayload
#valicao de erro
from pydantic import ValidationError

from app import db
from bson import ObjectId
from app.models.products import *
from app.models.sale import Sale
from app.decorators import token_required
from datetime import datetime, timedelta, timezone
import jwt
import csv
import os 
import io



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
@main_bp.route('/products/<string:product_id>', methods=['PUT'])
@token_required
def update_product(product_id):
    try:
        oid=ObjectId(product_id)
        update_data = UpdateProduct(**request.get_json())
    except ValidationError as e:
        return jsonify({"error":e.errors()})
    
    update_result = db.products.update_one(
        {"_id": oid},
        {"$set": update_data.model_dump(exclude_unset=True)}
    )
    if update_result.matched_count == 0:
        return jsonify({"error": "Produto não encontrado"}), 404

    update_product = db.products.find_one({"_id": oid})
    return jsonify(ProductDBMondel(**update_product).model_dump(by_alias=True, exclude=None))

#RF: O sistema deve permitir a delecao de um unico produto e produto existente
@main_bp.route('/products/<string:product_id>', methods=['DELETE'])
@token_required
def delete_product(token,product_id):
    try:
        oid = ObjectId(product_id)
    except Exception:
        return jsonify({"error": "id do produto invalido"})
    
    delete_product= db.products.delete_one({"_id": oid})

    if delete_product.deleted_count ==0:
        return jsonify({"error": "Produto não encontrado"}), 404

    return "",204

#RF: o sistema deve permitir a importacao de vendas atrave de um arquivo
@main_bp.route('/sales/upload', methods=['POST'])
@token_required
def upload_sales(token):
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files['file']

    if file.filename=='':
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400
    
    if file and file.filename.endswith('.csv'):
        csv_stream = io.StringIO(file.stream.read().decode('UTF-8'), newline=None)
        csv_reader =csv.DictReader(csv_stream)

        sales_to_insert = []
        error=[]

        for row_run, row in enumerate(csv_reader, 1):
            try:
                sale_data=Sale(**row)
                
                sales_to_insert.append(sale_data.model_dump())
            except ValidationError as e:
                error.append(f"Erro na linha {row_run} com dados invalido")

        if sales_to_insert:
            try:
                db.sales.insert_many(sales_to_insert)
            except Exception as e:
                return jsonify({'error': f'{e}'})
        return jsonify({
            "message": "Upload realizado com sucesso.",
            "vendas_importadas": len(sales_to_insert),
            "erros encontrado": error}),200
        

    return jsonify({"error": "Formato de arquivo inválido. Por favor, envie um arquivo CSV."}), 40   

@main_bp.route('/')
def index():
    return jsonify({"message": "Bem vindo ao Stylesync!"})



#escreve cada necessaridade de rota aqui dentro do blueprint main_bp
#com metico post
