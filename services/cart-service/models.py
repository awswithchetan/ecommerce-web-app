from pydantic import BaseModel
from typing import List
from datetime import datetime

class CartItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class Cart(BaseModel):
    user_id: str
    items: List[CartItem]
    updated_at: str

class AddItemRequest(BaseModel):
    product_id: str
    quantity: int
    price: float

class UpdateItemRequest(BaseModel):
    quantity: int
