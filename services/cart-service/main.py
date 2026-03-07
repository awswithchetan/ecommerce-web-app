from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from models import Cart, AddItemRequest, UpdateItemRequest
from database import get_carts_table
from datetime import datetime
from decimal import Decimal
import json

app = FastAPI(title="Cart Service")

def convert_floats_to_decimal(obj):
    """Convert float values to Decimal for DynamoDB"""
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj

def get_user_id_from_token(authorization: Optional[str] = Header(None)) -> str:
    """Extract user_id from JWT token. For local testing, use mock user_id"""
    if not authorization:
        # For local testing without real Cognito
        return "test-user-123"
    
    # In production, decode JWT and extract 'sub' claim
    # For now, simple mock
    return "test-user-123"

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "cart-service"}

@app.get("/cart", response_model=Cart)
def get_cart(user_id: str = Header(None, alias="X-User-Id")):
    """Get user's cart. X-User-Id header for testing, JWT in production"""
    if not user_id:
        user_id = "test-user-123"
    
    table = get_carts_table()
    response = table.get_item(Key={'user_id': user_id})
    
    if 'Item' not in response:
        # Return empty cart
        return Cart(user_id=user_id, items=[], updated_at=datetime.utcnow().isoformat())
    
    return response['Item']

@app.post("/cart/items")
def add_item(request: AddItemRequest, user_id: str = Header(None, alias="X-User-Id")):
    if not user_id:
        user_id = "test-user-123"
    
    table = get_carts_table()
    
    # Get current cart
    response = table.get_item(Key={'user_id': user_id})
    
    if 'Item' in response:
        items = response['Item']['items']
        # Check if product already in cart
        existing_item = next((item for item in items if item['product_id'] == request.product_id), None)
        if existing_item:
            existing_item['quantity'] += request.quantity
        else:
            items.append(convert_floats_to_decimal(request.dict()))
    else:
        items = [convert_floats_to_decimal(request.dict())]
    
    # Update cart
    table.put_item(Item={
        'user_id': user_id,
        'items': items,
        'updated_at': datetime.utcnow().isoformat()
    })
    
    return {"message": "Item added to cart", "user_id": user_id}

@app.put("/cart/items/{product_id}")
def update_item(product_id: str, request: UpdateItemRequest, user_id: str = Header(None, alias="X-User-Id")):
    if not user_id:
        user_id = "test-user-123"
    
    table = get_carts_table()
    response = table.get_item(Key={'user_id': user_id})
    
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = response['Item']['items']
    item = next((item for item in items if item['product_id'] == product_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    item['quantity'] = request.quantity
    
    table.put_item(Item={
        'user_id': user_id,
        'items': items,
        'updated_at': datetime.utcnow().isoformat()
    })
    
    return {"message": "Item updated"}

@app.delete("/cart/items/{product_id}")
def remove_item(product_id: str, user_id: str = Header(None, alias="X-User-Id")):
    if not user_id:
        user_id = "test-user-123"
    
    table = get_carts_table()
    response = table.get_item(Key={'user_id': user_id})
    
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = [item for item in response['Item']['items'] if item['product_id'] != product_id]
    
    table.put_item(Item={
        'user_id': user_id,
        'items': items,
        'updated_at': datetime.utcnow().isoformat()
    })
    
    return {"message": "Item removed"}

@app.delete("/cart")
def clear_cart(user_id: str = Header(None, alias="X-User-Id")):
    """Internal endpoint - called by Order Service after order creation"""
    if not user_id:
        user_id = "test-user-123"
    
    table = get_carts_table()
    table.delete_item(Key={'user_id': user_id})
    
    return {"message": "Cart cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
