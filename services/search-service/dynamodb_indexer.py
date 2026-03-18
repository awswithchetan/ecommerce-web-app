"""
DynamoDB Stream → OpenSearch Indexer Lambda

Paste this code directly into the Lambda inline editor.
No packaging required — uses only boto3 (pre-installed) and urllib (stdlib).

Environment variables required:
  OPENSEARCH_ENDPOINT  - e.g. https://search-xxx.us-west-2.es.amazonaws.com
  OPENSEARCH_USERNAME  - master username
  OPENSEARCH_PASSWORD  - master password
"""

import json
import os
import urllib.request
import urllib.error
import base64
import boto3

OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT'].rstrip('/')
USERNAME = os.environ['OPENSEARCH_USERNAME']
PASSWORD = os.environ['OPENSEARCH_PASSWORD']
INDEX_NAME = 'products'

AUTH = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()


def os_request(method, path, body=None):
    url = f"{OPENSEARCH_ENDPOINT}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Basic {AUTH}'
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"OpenSearch {method} {path} failed: {e.code} {e.read()}")


def deserialize(dynamo_item):
    d = boto3.dynamodb.types.TypeDeserializer()
    return {k: d.deserialize(v) for k, v in dynamo_item.items()}


def lambda_handler(event, context):
    for record in event.get('Records', []):
        event_name = record['eventName']

        if event_name in ('INSERT', 'MODIFY'):
            product = deserialize(record['dynamodb']['NewImage'])
            product_id = product['product_id']
            os_request('PUT', f'/{INDEX_NAME}/_doc/{product_id}', product)
            print(f"Indexed: {product_id}")

        elif event_name == 'REMOVE':
            product = deserialize(record['dynamodb']['OldImage'])
            product_id = product.get('product_id')
            if product_id:
                os_request('DELETE', f'/{INDEX_NAME}/_doc/{product_id}')
                print(f"Removed: {product_id}")
