# Project Structure

```
ecommerce-aws-tutorial/
│
├── README.md                          # Main project documentation
│
├── services/                          # Microservices
│   │
│   ├── product-service/              # Product catalog service
│   │   ├── main.py                   # FastAPI application
│   │   ├── config.py                 # Configuration settings
│   │   ├── models.py                 # Pydantic models
│   │   ├── database.py               # DynamoDB connection
│   │   ├── requirements.txt          # Python dependencies
│   │   ├── Dockerfile                # Container image
│   │   └── .env.example              # Environment variables template
│   │
│   ├── cart-service/                 # Shopping cart service
│   │   ├── main.py                   # FastAPI application
│   │   ├── config.py                 # Configuration settings
│   │   ├── models.py                 # Pydantic models
│   │   ├── database.py               # DynamoDB connection
│   │   ├── requirements.txt          # Python dependencies
│   │   ├── Dockerfile                # Container image
│   │   └── .env.example              # Environment variables template
│   │
│   ├── user-service/                 # User profile service
│   │   ├── main.py                   # FastAPI application
│   │   ├── config.py                 # Configuration settings
│   │   ├── models.py                 # Pydantic models
│   │   ├── database.py               # PostgreSQL connection
│   │   ├── requirements.txt          # Python dependencies
│   │   ├── Dockerfile                # Container image
│   │   └── .env.example              # Environment variables template
│   │
│   ├── order-service/                # Order processing service
│   │   ├── main.py                   # FastAPI application (orchestrator)
│   │   ├── config.py                 # Configuration settings
│   │   ├── models.py                 # Pydantic models
│   │   ├── database.py               # PostgreSQL connection
│   │   ├── requirements.txt          # Python dependencies
│   │   ├── Dockerfile                # Container image
│   │   └── .env.example              # Environment variables template
│   │
│   └── notification-service/         # Email notification service
│       ├── main.py                   # SQS consumer
│       ├── config.py                 # Configuration settings
│       ├── requirements.txt          # Python dependencies
│       ├── Dockerfile                # Container image
│       └── .env.example              # Environment variables template
│
├── frontend/                         # Frontend application (TODO)
│   └── react-app/                    # React application
│       └── (to be created)
│
├── local-deployment/                 # Local development setup
│   ├── docker-compose.yml            # Orchestrates all services locally
│   ├── nginx.conf                    # ALB simulator configuration
│   ├── test-local.sh                 # Automated testing script
│   └── localstack-init/              # LocalStack initialization
│       └── init.sh                   # Creates DynamoDB tables, SNS, SQS
│
├── aws-deployment/                   # AWS deployment resources (TODO)
│   ├── manual-steps/                 # Step-by-step guides
│   │   ├── 01-networking.md
│   │   ├── 02-databases.md
│   │   ├── 03-cognito.md
│   │   ├── 04-ecs.md
│   │   ├── 05-api-gateway.md
│   │   ├── 06-events.md
│   │   ├── 07-frontend.md
│   │   ├── 08-dns-ssl.md
│   │   └── 09-cleanup.md
│   │
│   └── terraform/                    # Infrastructure as Code (optional)
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       ├── vpc.tf
│       ├── ecs.tf
│       ├── rds.tf
│       ├── dynamodb.tf
│       └── (more terraform files)
│
└── docs/                             # Documentation
    ├── architecture.md               # Complete architecture overview
    ├── local-setup.md                # Local development guide
    └── aws-deployment.md             # AWS deployment guide (TODO)
```

## File Descriptions

### Services

Each service follows the same structure:

- **main.py**: FastAPI application with API endpoints
- **config.py**: Environment-based configuration using pydantic-settings
- **models.py**: Pydantic models for request/response validation
- **database.py**: Database connection and initialization
- **requirements.txt**: Python package dependencies
- **Dockerfile**: Multi-stage build for production container
- **.env.example**: Template for environment variables

### Local Deployment

- **docker-compose.yml**: Defines all services, networks, and volumes
- **nginx.conf**: Routes API requests to appropriate services (simulates ALB)
- **test-local.sh**: Automated end-to-end testing script
- **localstack-init/init.sh**: Initializes AWS resources in LocalStack

### Documentation

- **architecture.md**: Complete system architecture and design decisions
- **local-setup.md**: Step-by-step guide for local development
- **aws-deployment.md**: Manual AWS deployment guide (to be created)

## Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Product Service | 8001 | Product catalog APIs |
| Cart Service | 8002 | Shopping cart APIs |
| User Service | 8003 | User profile APIs |
| Order Service | 8004 | Order processing APIs |
| Notification Service | - | Background SQS consumer |
| Nginx (API Gateway) | 8080 | Unified API endpoint |
| PostgreSQL | 5432 | Database |
| LocalStack | 4566 | AWS services emulator |

## Database Schema

### DynamoDB Tables

**products**
```
product_id (String, PK)
name (String)
description (String)
price (Number)
stock (Number)
category (String)
image_url (String)
```

**carts**
```
user_id (String, PK)
items (List)
  - product_id (String)
  - quantity (Number)
  - price (Number)
updated_at (String)
```

### PostgreSQL Tables

**users**
```sql
id (SERIAL, PK)
cognito_sub (VARCHAR, UNIQUE)
email (VARCHAR, UNIQUE)
name (VARCHAR)
phone (VARCHAR)
address (TEXT)
created_at (TIMESTAMP)
```

**orders**
```sql
id (SERIAL, PK)
user_id (INTEGER, FK)
user_email (VARCHAR)
total_amount (DECIMAL)
status (VARCHAR)
created_at (TIMESTAMP)
```

**order_items**
```sql
id (SERIAL, PK)
order_id (INTEGER, FK)
product_id (VARCHAR)
quantity (INTEGER)
price (DECIMAL)
```

## API Endpoints

### Product Service (Port 8001)
- `GET /health` - Health check
- `GET /products` - List products (optional ?category filter)
- `GET /products/{id}` - Get product details
- `PUT /products/{id}/inventory` - Update inventory (internal)

### Cart Service (Port 8002)
- `GET /health` - Health check
- `GET /cart` - Get user's cart (requires X-User-Id header)
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{id}` - Update item quantity
- `DELETE /cart/items/{id}` - Remove item
- `DELETE /cart` - Clear cart (internal)

### User Service (Port 8003)
- `GET /health` - Health check
- `POST /users/profile` - Create user profile
- `GET /users/profile` - Get current user profile
- `PUT /users/profile` - Update profile
- `GET /users/{id}` - Get user by ID (internal)
- `GET /users/cognito/{sub}` - Get user by Cognito sub (internal)

### Order Service (Port 8004)
- `GET /health` - Health check
- `POST /orders` - Create order from cart
- `GET /orders` - Get user's orders
- `GET /orders/{id}` - Get order details

### Notification Service
- No HTTP endpoints (SQS consumer)

## Environment Variables

### Common
- `ENVIRONMENT` - local or aws
- `AWS_REGION` - AWS region

### DynamoDB Services (Product, Cart)
- `DYNAMODB_ENDPOINT` - LocalStack or AWS endpoint
- `{TABLE}_TABLE` - Table name

### RDS Services (User, Order)
- `DB_HOST` - PostgreSQL host
- `DB_PORT` - PostgreSQL port
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

### Order Service (Additional)
- `CART_SERVICE_URL` - Cart service endpoint
- `USER_SERVICE_URL` - User service endpoint
- `PRODUCT_SERVICE_URL` - Product service endpoint
- `SNS_ENDPOINT` - SNS endpoint
- `SNS_TOPIC_ARN` - SNS topic ARN

### Notification Service
- `SQS_ENDPOINT` - SQS endpoint
- `SES_ENDPOINT` - SES endpoint
- `SQS_QUEUE_URL` - SQS queue URL
- `SENDER_EMAIL` - Email sender address

## Next Steps

1. ✅ Backend services created
2. ✅ Local deployment setup created
3. ✅ Documentation created
4. ⏳ Create React frontend
5. ⏳ Create AWS deployment guides
6. ⏳ Create Terraform code (optional)
