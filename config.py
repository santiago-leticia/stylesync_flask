import os
from dotenv import load_dotenv
#sera responsavel por carregar as variaveis de ambiente do arquivo .env

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/stylesync_db')
    SECRET_KEY = os.getenv('SECRET_KEY')