from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson import ObjectId
from datetime import date

class Sale(BaseModel):
    sale_date: date
    product_id: int
    quantity: int
    total_value: float

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )