from fastapi import FastAPI, HTTPException, Header
from typing import List
from models import Order, OrderCreate, OrderItem
from database import get_db_cursor, init_db
from config import settings
import httpx
import boto3
import json

app = FastAPI(title="Order Service")

def get_sns_client():
    if settings.environment == "local":
        return boto3.client(
            'sns',
            endpoint_url=settings.sns_endpoint,
            region_name=settings.aws_region,
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
    else:
        return boto3.client('sns', region_name=settings.aws_region)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "order-service"}

@app.post("/orders", response_model=Order)
async def create_order(order: OrderCreate, user_id: str = Header(None, alias="X-User-Id")):
    """Create order from cart"""
    if not user_id:
        user_id = "test-user-123"  # Default for local testing
    
    async with httpx.AsyncClient() as client:
        # 1. Get user details
        try:
            user_response = await client.get(
                f"{settings.user_service_url}/users/cognito/{user_id}"
            )
            user_response.raise_for_status()
            user = user_response.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get user: {str(e)}")
        
        # 2. Get cart items
        try:
            cart_response = await client.get(
                f"{settings.cart_service_url}/cart",
                headers={"X-User-Id": user_id}
            )
            cart_response.raise_for_status()
            cart = cart_response.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get cart: {str(e)}")
        
        if not cart.get('items'):
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # 3. Calculate total and validate inventory
        total_amount = 0
        for item in cart['items']:
            total_amount += item['price'] * item['quantity']
            
            # Update inventory (reduce stock)
            try:
                inventory_response = await client.put(
                    f"{settings.product_service_url}/products/{item['product_id']}/inventory",
                    json={"quantity": -item['quantity']}
                )
                inventory_response.raise_for_status()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to update inventory: {str(e)}")
        
        # 4. Create order in database
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO orders (user_id, user_email, total_amount, status)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (user['id'], user['email'], total_amount, 'pending'))
            
            order_record = cursor.fetchone()
            order_id = order_record['id']
            
            # Insert order items
            for item in cart['items']:
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item['product_id'], item['quantity'], item['price']))
        
        # 5. Clear cart
        try:
            await client.delete(
                f"{settings.cart_service_url}/cart",
                headers={"X-User-Id": user_id}
            )
        except Exception as e:
            print(f"Warning: Failed to clear cart: {str(e)}")
        
        # 6. Publish SNS event
        try:
            sns = get_sns_client()
            message = {
                "order_id": order_id,
                "user_email": user['email'],
                "total_amount": float(total_amount),
                "items": cart['items']
            }
            sns.publish(
                TopicArn=settings.sns_topic_arn,
                Message=json.dumps(message),
                Subject="Order Created"
            )
        except Exception as e:
            print(f"Warning: Failed to publish SNS event: {str(e)}")
        
        # Return order with items
        order_dict = dict(order_record)
        order_dict['items'] = [
            OrderItem(product_id=item['product_id'], quantity=item['quantity'], price=item['price'])
            for item in cart['items']
        ]
        
        return order_dict

@app.get("/orders", response_model=List[Order])
async def get_user_orders(user_id: str = Header(None, alias="X-User-Id")):
    """Get all orders for a user"""
    if not user_id:
        user_id = "test-user-123"  # Default for local testing
    
    # First get user's internal ID
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.user_service_url}/users/cognito/{user_id}")
            response.raise_for_status()
            user = response.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get user: {str(e)}")
    
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (user['id'],))
        orders = cursor.fetchall()
        
        # Get items for each order
        result = []
        for order in orders:
            cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order['id'],))
            items = cursor.fetchall()
            
            order_dict = dict(order)
            order_dict['items'] = [
                OrderItem(product_id=item['product_id'], quantity=item['quantity'], price=item['price'])
                for item in items
            ]
            result.append(order_dict)
        
        return result

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    """Get order details"""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
        items = cursor.fetchall()
        
        order_dict = dict(order)
        order_dict['items'] = [
            OrderItem(product_id=item['product_id'], quantity=item['quantity'], price=item['price'])
            for item in items
        ]
        
        return order_dict

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
