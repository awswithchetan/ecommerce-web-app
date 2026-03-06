# Complete Application Testing Guide

## Quick Start

### Option 1: Full Stack with Docker Compose (Recommended)

```bash
cd local-deployment
docker-compose up --build
```

Then open http://localhost:3000 in your browser.

### Option 2: Backend in Docker, Frontend Standalone

```bash
# Terminal 1: Start backend
cd local-deployment
docker-compose up

# Terminal 2: Start frontend
cd frontend/react-app
npm install
npm start
```

Frontend: http://localhost:3000
API: http://localhost:8080

## Testing the Application

### Via Web Browser (Easiest)

1. **Open the app**: http://localhost:3000

2. **Browse Products**
   - You'll see 3 sample products (Laptop, Mouse, Keyboard)
   - Each shows price and stock

3. **Add to Cart**
   - Click "Add to Cart" on any product
   - See success message

4. **View Cart**
   - Click "Cart" in navigation
   - See your items
   - Can remove items

5. **Place Order**
   - Click "Place Order" button
   - Order is created
   - Cart is cleared

6. **View Orders**
   - Click "Orders" in navigation
   - See your order history

### Via API (curl)

```bash
# 1. List products
curl http://localhost:8080/api/products

# 2. Create user (first time only)
curl -X POST http://localhost:8080/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "cognito_sub": "test-user-123",
    "email": "test@example.com",
    "name": "Test User"
  }'

# 3. Add to cart
curl -X POST http://localhost:8080/api/cart/items \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user-123" \
  -d '{"product_id":"prod-001","quantity":1,"price":999.99}'

# 4. View cart
curl -H "X-User-Id: test-user-123" http://localhost:8080/api/cart

# 5. Place order
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user-123" \
  -d '{}'

# 6. View orders
curl -H "X-User-Id: test-user-123" http://localhost:8080/api/orders
```

### Automated Test Script

```bash
cd local-deployment
./test-local.sh
```

## Verifying Backend Services

### Check Service Health

```bash
curl http://localhost:8001/health  # Product Service
curl http://localhost:8002/health  # Cart Service
curl http://localhost:8003/health  # User Service
curl http://localhost:8004/health  # Order Service
```

### Check DynamoDB Tables

```bash
# Install awslocal
pip install awscli-local

# List tables
awslocal dynamodb list-tables

# View products
awslocal dynamodb scan --table-name products

# View carts
awslocal dynamodb scan --table-name carts
```

### Check PostgreSQL

```bash
# Connect to database
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

### Check Event Flow (SNS/SQS)

```bash
# Check notification service logs
docker-compose logs notification-service

# Check if messages are in queue
awslocal sqs receive-message \
  --queue-url http://localhost:4566/000000000000/notification-queue
```

## Complete End-to-End Test

### Scenario: Customer Orders a Laptop

1. **User visits website** → React app loads from port 3000
2. **Browse products** → API call to Product Service → DynamoDB
3. **Add laptop to cart** → API call to Cart Service → DynamoDB
4. **View cart** → Shows laptop with price
5. **Place order** → Order Service orchestrates:
   - Gets user email from User Service (PostgreSQL)
   - Gets cart items from Cart Service (DynamoDB)
   - Updates inventory in Product Service (DynamoDB)
   - Creates order in PostgreSQL
   - Clears cart
   - Publishes event to SNS
6. **SNS → SQS** → Message queued
7. **Notification Service** → Polls SQS → Sends email via SES
8. **View orders** → Shows completed order

### Expected Results

✅ Product stock reduced by 1
✅ Cart is empty
✅ Order appears in orders page
✅ Order stored in PostgreSQL
✅ Email notification logged (check notification-service logs)

## Troubleshooting

### Frontend won't start

```bash
cd frontend/react-app
rm -rf node_modules package-lock.json
npm install
npm start
```

### API calls failing (CORS)

Check that backend services are running:
```bash
docker-compose ps
```

### Services not responding

```bash
# Restart all services
docker-compose restart

# Or rebuild
docker-compose down
docker-compose up --build
```

### Port conflicts

If ports 3000, 8080, 8001-8004, 5432, or 4566 are in use:
- Stop conflicting services
- Or modify ports in docker-compose.yml

## Performance Testing

### Load Test with curl

```bash
# Add 100 items to cart
for i in {1..100}; do
  curl -X POST http://localhost:8080/api/cart/items \
    -H "Content-Type: application/json" \
    -H "X-User-Id: test-user-$i" \
    -d '{"product_id":"prod-001","quantity":1,"price":999.99}'
done
```

## What's Working

✅ Complete microservices architecture
✅ Service-to-service communication
✅ Event-driven notifications
✅ React frontend with routing
✅ Full order flow
✅ Local testing without AWS
✅ Production-ready code

## Next Steps

1. **Test locally** - Verify everything works
2. **AWS Deployment** - Follow manual deployment guides (coming soon)
3. **Add Cognito** - Real authentication
4. **Terraform** - Automate infrastructure (optional)

## Access Points

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **Product Service**: http://localhost:8001
- **Cart Service**: http://localhost:8002
- **User Service**: http://localhost:8003
- **Order Service**: http://localhost:8004
- **PostgreSQL**: localhost:5432
- **LocalStack**: http://localhost:4566

## API Documentation

Each service has auto-generated docs:
- http://localhost:8001/docs (Product Service)
- http://localhost:8002/docs (Cart Service)
- http://localhost:8003/docs (User Service)
- http://localhost:8004/docs (Order Service)
