import boto3
from config import settings

def get_dynamodb_resource():
    if settings.environment == "local":
        return boto3.resource(
            'dynamodb',
            endpoint_url=settings.dynamodb_endpoint,
            region_name=settings.aws_region,
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
    else:
        return boto3.resource('dynamodb', region_name=settings.aws_region)

def get_carts_table():
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.carts_table)
