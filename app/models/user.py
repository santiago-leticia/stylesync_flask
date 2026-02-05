from pydantic import BaseModel

class LoginPayload(BaseModel):
    username: str
    password: str
    #a funcao disso aqui e definir o modelo de dados do login