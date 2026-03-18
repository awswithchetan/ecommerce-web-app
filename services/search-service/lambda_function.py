import json
import boto3
import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

OPENSEARCH_ENDPOINT = os.environ.get('OPENSEARCH_ENDPOINT', '')
INDEX_NAME = 'products'
REGION = os.environ.get('AWS_REGION', 'us-east-1')


def get_opensearch_client():
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        REGION,
        'es',
        session_token=credentials.token
    )
    return OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def search_handler(event, context):
    """Handles search requests from ALB."""
    params = event.get('queryStringParameters') or {}
    query = params.get('q', '').strip()
    category = params.get('category', '').strip()

    if not query and not category:
        return alb_response(400, {'error': 'Query parameter "q" or "category" is required'})

    try:
        client = get_opensearch_client()

        must_clauses = []
        if query:
            must_clauses.append({
                'multi_match': {
                    'query': query,
                    'fields': ['name^3', 'description', 'category'],
                    'fuzziness': 'AUTO'
                }
            })
        if category:
            must_clauses.append({'term': {'category.keyword': category}})

        body = {
            'query': {'bool': {'must': must_clauses}},
            'size': 50
        }

        response = client.search(index=INDEX_NAME, body=body)
        hits = [hit['_source'] for hit in response['hits']['hits']]
        return alb_response(200, hits)

    except Exception as e:
        print(f"Search error: {e}")
        return alb_response(500, {'error': 'Search failed'})


def indexer_handler(event, context):
    """Handles DynamoDB Stream events to keep OpenSearch index in sync."""
    client = get_opensearch_client()

    for record in event.get('Records', []):
        event_name = record['eventName']  # INSERT, MODIFY, REMOVE

        if event_name in ('INSERT', 'MODIFY'):
            new_image = record['dynamodb'].get('NewImage', {})
            product = deserialize(new_image)
            client.index(index=INDEX_NAME, id=product['product_id'], body=product)
            print(f"Indexed product: {product['product_id']}")

        elif event_name == 'REMOVE':
            old_image = record['dynamodb'].get('OldImage', {})
            product_id = old_image.get('product_id', {}).get('S')
            if product_id:
                client.delete(index=INDEX_NAME, id=product_id, ignore=[404])
                print(f"Removed product from index: {product_id}")


def deserialize(dynamo_item):
    """Convert DynamoDB typed JSON to plain dict."""
    deserializer = boto3.dynamodb.types.TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_item.items()}


def alb_response(status_code, body):
    return {
        'statusCode': status_code,
        'statusDescription': f'{status_code} OK' if status_code == 200 else f'{status_code}',
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }
