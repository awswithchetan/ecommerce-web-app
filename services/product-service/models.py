from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    product_id: str
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None

class UpdateInventoryRequest(BaseModel):
    quantity: int  # Positive to add, negative to reduce
