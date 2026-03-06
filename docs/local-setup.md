# Local Development Setup

This guide will help you run the entire eCommerce application locally using Docker Compose and LocalStack.

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available for Docker
- Ports 4566, 5432, 8001-8004, 8080 available

## Architecture (Local)

```
┌─────────────────────────────────────────────────────────┐
│                    Your Machine                          │
│                                                          │
│  ┌──────────────┐                                       │
│  │   Nginx      │  Port 8080 (API Gateway simulator)   │
│  │  (ALB sim)   │                                       │
│  └──────┬───────┘                                       │
│         │                                                │
│    ┌────┴────┬────────┬────────┬────────┐              │
│    │         │        │        │        │               │
│  ┌─▼──┐   ┌─▼──┐  ┌─▼──┐  ┌─▼──┐  ┌─▼──────┐         │
│  │Prod│   │Cart│  │User│  │Ordr│  │Notif   │         │
│  │Svc │   │Svc │  │Svc │  │Svc │  │Svc     │         │
│  └─┬──┘   └─┬──┘  └─┬──┘  └─┬──┘  └─┬──────┘         │
│    │        │        │        │        │                │
│  ┌─▼────────▼────┐ ┌─▼────────▼────┐ ┌─▼──────────┐   │
│  │  LocalStack   │ │   PostgreSQL  │ │ LocalStack │   │
│  │  (DynamoDB)   │ │               │ │ (SNS/SQS)  │   │
│  └───────────────┘ └───────────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Navigate to local-deployment directory

```bash
cd local-deployment
```

### 2. Start all services

```bash
docker-compose up --build
```

This will:
- Start LocalStack (DynamoDB, SNS, SQS, SES)
- Start PostgreSQL
- Build and start all 5 microservices
- Start Nginx as API gateway
- Initialize DynamoDB tables with sample products
- Create SNS topic and SQS queue

### 3. Wait for services to be ready

Watch the logs until you see:
```
localstack_1           | LocalStack initialization complete!
product-service_1      | INFO:     Application startup complete.
cart-service_1         | INFO:     Application startup complete.
user-service_1         | INFO:     Application startup complete.
order-service_1        | INFO:     Application startup complete.
notification-service_1 | Notification Service started. Polling queue...
```

## Testing the Application

### 1. Check health of all services

```bash
# Via Nginx (API Gateway)
curl http://localhost:8080/health

# Individual services
curl http://localhost:8001/health  # Product Service
curl http://localhost:8002/health  # Cart Service
curl http://localhost:8003/health  # User Service
curl http://localhost:8004/health  # Order Service
```

### 2. Browse products

```bash
curl http://localhost:8080/api/products
```

You should see 3 sample products (Laptop, Mouse, Keyboard).

### 3. Create a user

```bash
curl -X POST http://localhost:8080/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "cognito_sub": "test-user-123",
    "email": "test@example.com",
    "name": "Test User",
    "phone": "+1234567890",
    "address": "123 Test St"
  }'
```

### 4. Add items to cart

```bash
# Add laptop to cart
curl -X POST http://localhost:8080/api/cart/items \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user-123" \
  -d '{
    "product_id": "prod-001",
    "quantity": 1,
    "price": 999.99
  }'

# Add mouse to cart
curl -X POST http://localhost:8080/api/cart/items \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user-123" \
  -d '{
    "product_id": "prod-002",
    "quantity": 2,
    "price": 29.99
  }'
```

### 5. View cart

```bash
curl -H "X-User-Id: test-user-123" \
  http://localhost:8080/api/cart
```

### 6. Place an order

```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user-123" \
  -d '{}'
```

This will:
1. Get user details from User Service
2. Get cart items from Cart Service
3. Update inventory in Product Service
4. Create order in PostgreSQL
5. Clear the cart
6. Publish event to SNS
7. Notification Service receives message from SQS
8. "Email" is logged (check notification-service logs)

### 7. Check notification logs

```bash
docker-compose logs notification-service
```

You should see the order confirmation email content.

### 8. View orders

```bash
curl -H "X-User-Id: test-user-123" \
  http://localhost:8080/api/orders
```

## Accessing Services Directly

- **API Gateway (Nginx)**: http://localhost:8080
- **Product Service**: http://localhost:8001
- **Cart Service**: http://localhost:8002
- **User Service**: http://localhost:8003
- **Order Service**: http://localhost:8004
- **PostgreSQL**: localhost:5432 (user: postgres, password: postgres, db: ecommerce_db)
- **LocalStack**: http://localhost:4566

## Inspecting LocalStack Resources

Install AWS CLI and use `awslocal` wrapper:

```bash
# Install awslocal
pip install awscli-local

# List DynamoDB tables
awslocal dynamodb list-tables

# Scan products table
awslocal dynamodb scan --table-name products

# List SNS topics
awslocal sns list-topics

# List SQS queues
awslocal sqs list-queues
```

## Inspecting PostgreSQL

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d ecommerce_db

# View users
SELECT * FROM users;

# View orders
SELECT * FROM orders;

# View order items
SELECT * FROM order_items;

# Exit
\q
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Troubleshooting

### Services not starting

```bash
# Check logs
docker-compose logs <service-name>

# Rebuild specific service
docker-compose up --build <service-name>
```

### LocalStack not initializing

```bash
# Check LocalStack logs
docker-compose logs localstack

# Manually run init script
docker-compose exec localstack bash /etc/localstack/init/ready.d/init.sh
```

### Port conflicts

If ports are already in use, modify `docker-compose.yml` to use different ports.

## Next Steps

Once you've verified everything works locally:
1. Review the service code to understand the implementation
2. Proceed to AWS deployment guide
3. Learn how to deploy this to real AWS infrastructure

## Development Tips

- Services auto-reload on code changes (if you mount volumes)
- Use Postman collection (coming soon) for easier testing
- Check individual service logs for debugging
- LocalStack persists data in volumes between restarts
