from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "local"
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "ecommerce_db"
    db_user: str = "postgres"
    db_password: str = "postgres"
    
    # Service URLs
    cart_service_url: str = "http://cart-service:8002"
    user_service_url: str = "http://user-service:8003"
    product_service_url: str = "http://product-service:8001"
    
    # AWS
    aws_region: str = "us-east-1"
    sns_endpoint: str = "http://localstack:4566"
    sns_topic_arn: str = "arn:aws:sns:us-east-1:000000000000:order-events"
    
    class Config:
        env_file = ".env"

settings = Settings()
