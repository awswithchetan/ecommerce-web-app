import os
import boto3
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(frozen=False, env_file=".env")
    environment: str = "local"

    aws_region: str = "us-east-1"
    opensearch_endpoint: str = "http://localhost:9200"
    opensearch_username: str = "admin"
    opensearch_password: str = "admin"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.environment != "local":
            self._load_from_parameter_store()

    def _load_from_parameter_store(self):
        try:
            region = os.getenv('AWS_REGION', 'us-east-1')
            ssm = boto3.client('ssm', region_name=region)
            response = ssm.get_parameters(
                Names=[
                    f'/ecommerce/{self.environment}/aws/region',
                    f'/ecommerce/{self.environment}/opensearch/endpoint',
                    f'/ecommerce/{self.environment}/opensearch/username',
                    f'/ecommerce/{self.environment}/opensearch/password',
                ],
                WithDecryption=True
            )
            for param in response['Parameters']:
                name = param['Name']
                value = param['Value']
                if name.endswith('/aws/region'):
                    self.aws_region = value
                elif name.endswith('/opensearch/endpoint'):
                    self.opensearch_endpoint = value
                elif name.endswith('/opensearch/username'):
                    self.opensearch_username = value
                elif name.endswith('/opensearch/password'):
                    self.opensearch_password = value
        except Exception as e:
            print(f"Warning: Could not load parameters from Parameter Store: {e}")

settings = Settings()
