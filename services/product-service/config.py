from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "local"
    aws_region: str = "us-east-1"
    dynamodb_endpoint: str = "http://localstack:4566"
    products_table: str = "products"
    
    class Config:
        env_file = ".env"

settings = Settings()
