from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import Product, UpdateInventoryRequest
from database import get_products_table
from boto3.dynamodb.conditions import Attr
import uuid

app = FastAPI(title="Product Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "product-service"}

@app.get("/products", response_model=List[Product])
def list_products(category: str = None):
    table = get_products_table()
    
    if category:
        response = table.scan(FilterExpression=Attr('category').eq(category))
    else:
        response = table.scan()
    
    return response.get('Items', [])

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    table = get_products_table()
    response = table.get_item(Key={'product_id': product_id})
    
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return response['Item']

@app.put("/products/{product_id}/inventory")
def update_inventory(product_id: str, request: UpdateInventoryRequest):
    """Internal endpoint - called by Order Service to update stock"""
    table = get_products_table()
    
    try:
        response = table.update_item(
            Key={'product_id': product_id},
            UpdateExpression="SET stock = stock + :qty",
            ExpressionAttributeValues={':qty': request.quantity},
            ReturnValues="UPDATED_NEW"
        )
        return {"product_id": product_id, "new_stock": response['Attributes']['stock']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
