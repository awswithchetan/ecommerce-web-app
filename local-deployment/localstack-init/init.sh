#!/bin/bash

echo "Initializing LocalStack resources..."

# Wait for LocalStack to be ready
sleep 5

# Create DynamoDB tables
echo "Creating DynamoDB tables..."

awslocal dynamodb create-table \
    --table-name products \
    --attribute-definitions AttributeName=product_id,AttributeType=S \
    --key-schema AttributeName=product_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

awslocal dynamodb create-table \
    --table-name carts \
    --attribute-definitions AttributeName=user_id,AttributeType=S \
    --key-schema AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# Seed products table
echo "Seeding products..."

awslocal dynamodb put-item \
    --table-name products \
    --item '{
        "product_id": {"S": "prod-001"},
        "name": {"S": "Laptop"},
        "description": {"S": "High-performance laptop"},
        "price": {"N": "999.99"},
        "stock": {"N": "50"},
        "category": {"S": "Electronics"},
        "image_url": {"S": "https://placehold.co/300x200/2196F3/white?text=Laptop"}
    }'

awslocal dynamodb put-item \
    --table-name products \
    --item '{
        "product_id": {"S": "prod-002"},
        "name": {"S": "Wireless Mouse"},
        "description": {"S": "Ergonomic wireless mouse"},
        "price": {"N": "29.99"},
        "stock": {"N": "200"},
        "category": {"S": "Electronics"},
        "image_url": {"S": "https://placehold.co/300x200/4CAF50/white?text=Mouse"}
    }'

awslocal dynamodb put-item \
    --table-name products \
    --item '{
        "product_id": {"S": "prod-003"},
        "name": {"S": "Mechanical Keyboard"},
        "description": {"S": "RGB mechanical keyboard"},
        "price": {"N": "79.99"},
        "stock": {"N": "100"},
        "category": {"S": "Electronics"},
        "image_url": {"S": "https://placehold.co/300x200/FF9800/white?text=Keyboard"}
    }'

# Create SNS topic
echo "Creating SNS topic..."
awslocal sns create-topic --name order-events

# Create SQS queue
echo "Creating SQS queue..."
awslocal sqs create-queue --queue-name notification-queue

# Subscribe SQS to SNS
echo "Subscribing SQS to SNS..."
awslocal sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:000000000000:order-events \
    --protocol sqs \
    --notification-endpoint arn:aws:sqs:us-east-1:000000000000:notification-queue

echo "LocalStack initialization complete!"
