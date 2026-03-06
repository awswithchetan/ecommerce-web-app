from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "local"
    aws_region: str = "us-east-1"
    dynamodb_endpoint: str = "http://localstack:4566"
    carts_table: str = "carts"
    
    class Config:
        env_file = ".env"

settings = Settings()
