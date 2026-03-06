# Quick Reference Guide

## Local Development Commands

### Start/Stop Services

```bash
# Start all services
cd local-deployment
docker-compose up --build

# Start in background
docker-compose up -d --build

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f product-service
docker-compose logs -f notification-service
```

### Testing

```bash
# Run automated tests
cd local-deployment
./test-local.sh

# Manual API testing
curl http://localhost:8080/api/products
curl http://localhost:8080/api/cart -H "X-User-Id: test-123"
```

### Database Access

```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres -d ecommerce_db

# Inside psql
\dt                    # List tables
SELECT * FROM users;
SELECT * FROM orders;
\q                     # Quit

# DynamoDB (requires awslocal)
pip install awscli-local
awslocal dynamodb list-tables
awslocal dynamodb scan --table-name products
awslocal dynamodb scan --table-name carts
```

### LocalStack

```bash
# List SNS topics
awslocal sns list-topics

# List SQS queues
awslocal sqs list-queues

# Check SQS messages
awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/notification-queue
```

## API Endpoints

### Base URL (Local)
```
http://localhost:8080/api
```

### Products

```bash
# List all products
GET /products

# Get product by ID
GET /products/{product_id}

# Example
curl http://localhost:8080/api/products
curl http://localhost:8080/api/products/prod-001
```

### Cart (Requires X-User-Id header)

```bash
# Get cart
GET /cart
Header: X-User-Id: {user_id}

# Add item
POST /cart/items
Header: X-User-Id: {user_id}
Body: {"product_id": "prod-001", "quantity": 1, "price": 999.99}

# Update item
PUT /cart/items/{product_id}
Header: X-User-Id: {user_id}
Body: {"quantity": 2}

# Remove item
DELETE /cart/items/{product_id}
Header: X-User-Id: {user_id}

# Examples
curl -H "X-User-Id: test-123" http://localhost:8080/api/cart

curl -X POST http://localhost:8080/api/cart/items \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-123" \
  -d '{"product_id":"prod-001","quantity":1,"price":999.99}'
```

### Users

```bash
# Create user profile
POST /users/profile
Body: {
  "cognito_sub": "test-123",
  "email": "test@example.com",
  "name": "Test User",
  "phone": "+1234567890",
  "address": "123 Test St"
}

# Get profile
GET /users/profile
Header: X-User-Id: {cognito_sub}

# Update profile
PUT /users/profile
Header: X-User-Id: {cognito_sub}
Body: {"name": "Updated Name", "phone": "+9876543210"}

# Examples
curl -X POST http://localhost:8080/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{"cognito_sub":"test-123","email":"test@example.com","name":"Test User"}'

curl -H "X-User-Id: test-123" http://localhost:8080/api/users/profile
```

### Orders (Requires X-User-Id header)

```bash
# Create order (from cart)
POST /orders
Header: X-User-Id: {user_id}
Body: {}

# Get user's orders
GET /orders
Header: X-User-Id: {user_id}

# Get specific order
GET /orders/{order_id}

# Examples
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-123" \
  -d '{}'

curl -H "X-User-Id: test-123" http://localhost:8080/api/orders
```

## Service URLs (Direct Access)

| Service | URL | Docs |
|---------|-----|------|
| Product Service | http://localhost:8001 | http://localhost:8001/docs |
| Cart Service | http://localhost:8002 | http://localhost:8002/docs |
| User Service | http://localhost:8003 | http://localhost:8003/docs |
| Order Service | http://localhost:8004 | http://localhost:8004/docs |
| API Gateway (Nginx) | http://localhost:8080 | - |

## Sample Data

### Products (Pre-seeded)

```json
{
  "product_id": "prod-001",
  "name": "Laptop",
  "price": 999.99,
  "stock": 50,
  "category": "Electronics"
}

{
  "product_id": "prod-002",
  "name": "Wireless Mouse",
  "price": 29.99,
  "stock": 200,
  "category": "Electronics"
}

{
  "product_id": "prod-003",
  "name": "Mechanical Keyboard",
  "price": 79.99,
  "stock": 100,
  "category": "Electronics"
}
```

## Complete User Flow Example

```bash
# 1. Create user
curl -X POST http://localhost:8080/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "cognito_sub": "user-001",
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "+1234567890",
    "address": "123 Main St, City, State"
  }'

# 2. Browse products
curl http://localhost:8080/api/products

# 3. Add laptop to cart
curl -X POST http://localhost:8080/api/cart/items \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user-001" \
  -d '{"product_id":"prod-001","quantity":1,"price":999.99}'

# 4. Add mouse to cart
curl -X POST http://localhost:8080/api/cart/items \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user-001" \
  -d '{"product_id":"prod-002","quantity":2,"price":29.99}'

# 5. View cart
curl -H "X-User-Id: user-001" http://localhost:8080/api/cart

# 6. Place order
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user-001" \
  -d '{}'

# 7. View orders
curl -H "X-User-Id: user-001" http://localhost:8080/api/orders

# 8. Check notification logs
docker-compose logs notification-service | tail -20
```

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Rebuild specific service
docker-compose up --build product-service

# Clean restart
docker-compose down -v
docker-compose up --build
```

### LocalStack not initializing

```bash
# Check LocalStack logs
docker-compose logs localstack

# Manually run init script
docker-compose exec localstack bash /etc/localstack/init/ready.d/init.sh

# Verify tables created
awslocal dynamodb list-tables
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Port conflicts

```bash
# Check what's using a port
lsof -i :8080
lsof -i :5432

# Kill process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

## Environment Variables

### For Local Development

All services use these defaults (already configured in docker-compose.yml):

```bash
ENVIRONMENT=local
AWS_REGION=us-east-1
DYNAMODB_ENDPOINT=http://localstack:4566
SNS_ENDPOINT=http://localstack:4566
SQS_ENDPOINT=http://localstack:4566
SES_ENDPOINT=http://localstack:4566
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=postgres
```

### For AWS Deployment

Change these when deploying to AWS:

```bash
ENVIRONMENT=aws
AWS_REGION=us-east-1
# Remove all *_ENDPOINT variables (use real AWS)
DB_HOST=<rds-endpoint>
DB_PASSWORD=<secure-password>
SNS_TOPIC_ARN=<real-sns-arn>
SQS_QUEUE_URL=<real-sqs-url>
```

## Useful Docker Commands

```bash
# View running containers
docker-compose ps

# Restart a service
docker-compose restart product-service

# Rebuild a service
docker-compose up -d --build product-service

# Execute command in container
docker-compose exec product-service bash

# View resource usage
docker stats

# Clean up everything
docker-compose down -v --rmi all
```

## Health Checks

```bash
# Check all services
curl http://localhost:8001/health  # Product
curl http://localhost:8002/health  # Cart
curl http://localhost:8003/health  # User
curl http://localhost:8004/health  # Order
curl http://localhost:8080/health  # Nginx

# Or use the test script
cd local-deployment
./test-local.sh
```

## Next Steps

1. **Local Testing**: Follow `docs/local-setup.md`
2. **AWS Deployment**: Follow `docs/aws-deployment.md` (coming soon)
3. **Frontend**: Build React app (coming soon)
4. **IaC**: Use Terraform for automation (coming soon)
