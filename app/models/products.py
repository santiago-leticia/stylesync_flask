from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson import ObjectId

class Produt(BaseModel):
    id: Optional[ObjectId]= Field(None, alias='_id')
    name: str
    price: float
    description: Optional[str] = None
    stock: int
    #a funcao disso aqui e definir o modelo de dados do produto

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class ProductDBMondel(Produt):
    def model_dump(self, *, mode = 'python', include = None, exclude = None, context = None, by_alias = None, exclude_unset = False, exclude_defaults = False, exclude_none = False, exclude_computed_fields = False, round_trip = False, warnings = True, fallback = None, serialize_as_any = False):
        data= super().model_dump(mode=mode, include=include, exclude=exclude, context=context, by_alias=by_alias, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none, exclude_computed_fields=exclude_computed_fields, round_trip=round_trip, warnings=warnings, fallback=fallback, serialize_as_any=serialize_as_any)
        if self.id:
            data['_id']= str(self.id)
        return data
    #essa classe e para converter o id do produto de ObjectId para string quando for retornarndo a resposta da API

class UpdateProduct(BaseModel):
    name: Optional[str]= None
    price: Optional[float] = None
    description: Optional[str] = None
    stock: Optional[int] = None
    #a funcao disso aqui e definir o modelo de dados do produto

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )    