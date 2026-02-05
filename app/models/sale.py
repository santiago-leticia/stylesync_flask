from pydantic import BaseModel
from datetime import date

class Sale(BaseModel):
    sale_date: date
    product_id: int
    quantity: int
    total_value: float