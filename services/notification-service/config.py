from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "local"
    aws_region: str = "us-east-1"
    sqs_endpoint: str = "http://localstack:4566"
    ses_endpoint: str = "http://localstack:4566"
    sqs_queue_url: str = "http://localstack:4566/000000000000/notification-queue"
    sender_email: str = "noreply@ecommerce.com"
    
    class Config:
        env_file = ".env"

settings = Settings()
