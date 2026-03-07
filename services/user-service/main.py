from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from models import User, UserCreate, UserUpdate
from database import get_db_cursor, init_db

app = FastAPI(title="User Service")

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "user-service"}

@app.post("/users/profile", response_model=User)
def create_user(user: UserCreate):
    """Create user profile after Cognito registration"""
    with get_db_cursor() as cursor:
        try:
            cursor.execute("""
                INSERT INTO users (cognito_sub, email, name, phone, address)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """, (user.cognito_sub, user.email, user.name, user.phone, user.address))
            
            result = cursor.fetchone()
            return result
        except Exception as e:
            if "duplicate key" in str(e):
                raise HTTPException(status_code=400, detail="User already exists")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/profile", response_model=User)
def get_profile(user_id: str = Header(None, alias="X-User-Id")):
    """Get current user's profile"""
    if not user_id:
        user_id = "test-user-123"  # Default for local testing
    
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE cognito_sub = %s", (user_id,))
        result = cursor.fetchone()
        
        if not result:
            # Auto-create user if they don't exist
            cursor.execute("""
                INSERT INTO users (cognito_sub, email, name)
                VALUES (%s, %s, %s)
                RETURNING *
            """, (user_id, f"{user_id}@example.com", user_id))
            result = cursor.fetchone()
        
        return result

@app.put("/users/profile", response_model=User)
def update_profile(updates: UserUpdate, user_id: str = Header(None, alias="X-User-Id")):
    """Update user profile"""
    if not user_id:
        user_id = "test-user-123"  # Default for local testing
    
    update_fields = []
    values = []
    
    if updates.name is not None:
        update_fields.append("name = %s")
        values.append(updates.name)
    if updates.phone is not None:
        update_fields.append("phone = %s")
        values.append(updates.phone)
    if updates.address is not None:
        update_fields.append("address = %s")
        values.append(updates.address)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    values.append(user_id)
    
    with get_db_cursor() as cursor:
        cursor.execute(f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE cognito_sub = %s
            RETURNING *
        """, values)
        
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result

@app.get("/users/{user_id}", response_model=User)
def get_user_by_id(user_id: int):
    """Internal endpoint - get user by ID (called by Order Service)"""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result

@app.get("/users/cognito/{cognito_sub}", response_model=User)
def get_user_by_cognito_sub(cognito_sub: str):
    """Internal endpoint - get user by Cognito sub (called by Order Service)"""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE cognito_sub = %s", (cognito_sub,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
