from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    pass  # Will get items from cart

class Order(BaseModel):
    id: int
    user_id: int
    user_email: str
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItem] = []
