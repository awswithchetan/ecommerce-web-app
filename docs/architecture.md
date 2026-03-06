# eCommerce Application Architecture

## Overview

This is a production-grade microservices-based eCommerce application built on AWS, designed as a hands-on tutorial for learning AWS services and cloud architecture patterns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Internet                                    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      Route 53           │
                    │   (DNS Management)      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     CloudFront          │
                    │  (CDN + SSL/TLS)        │
                    └─────┬──────────────┬────┘
                          │              │
                ┌─────────▼──┐      ┌───▼──────────────┐
                │    S3      │      │  API Gateway     │
                │  (React)   │      │  (HTTP API)      │
                └────────────┘      └───┬──────────────┘
                                        │
                                   ┌────▼────────┐
                                   │  VPC Link   │
                                   └────┬────────┘
                                        │
┌───────────────────────────────────────┼─────────────────────────────────┐
│                                  VPC  │                                  │
│                                       │                                  │
│                          ┌────────────▼────────────┐                    │
│                          │  Application Load       │                    │
│                          │  Balancer (Private)     │                    │
│                          └─┬────┬────┬────┬───────┘                    │
│                            │    │    │    │                             │
│              ┌─────────────┼────┼────┼────┼─────────────┐              │
│              │  ECS Cluster│    │    │    │             │              │
│              │             │    │    │    │             │              │
│              │  ┌──────────▼┐ ┌─▼────▼──┐ ┌▼──────────┐ │             │
│              │  │ Product   │ │  Cart   │ │   User    │ │             │
│              │  │ Service   │ │ Service │ │  Service  │ │             │
│              │  │ (Fargate) │ │(Fargate)│ │ (Fargate) │ │             │
│              │  └─────┬─────┘ └────┬────┘ └─────┬─────┘ │             │
│              │        │            │            │        │             │
│              │  ┌─────▼────────────▼────────────▼─────┐ │             │
│              │  │         Order Service               │ │             │
│              │  │          (Fargate)                  │ │             │
│              │  └──────────────┬──────────────────────┘ │             │
│              │                 │                         │             │
│              │  ┌──────────────▼──────────────────────┐ │             │
│              │  │    Notification Service             │ │             │
│              │  │         (Fargate)                   │ │             │
│              │  └─────────────────────────────────────┘ │             │
│              └─────────────────────────────────────────────┘           │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │   DynamoDB       │  │   RDS            │  │  Cognito         │   │
│  │                  │  │  PostgreSQL      │  │  User Pool       │   │
│  │  - products      │  │                  │  │                  │   │
│  │  - carts         │  │  - users         │  └──────────────────┘   │
│  │                  │  │  - orders        │                          │
│  └──────────────────┘  │  - order_items   │                          │
│                        └──────────────────┘                          │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │      SNS         │  │      SQS         │  │      SES         │   │
│  │  order-events    │─▶│ notification-    │─▶│  Email Sending   │   │
│  │    (Topic)       │  │     queue        │  │                  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Services

### 1. Product Service
**Purpose**: Manage product catalog

**Technology**: Python FastAPI

**Data Store**: DynamoDB
- Table: `products`
- Key: `product_id`

**APIs**:
- `GET /products` - List all products (with optional category filter)
- `GET /products/{id}` - Get product details
- `PUT /products/{id}/inventory` - Update stock (internal)

**AWS Services**: ECS/Fargate, DynamoDB

---

### 2. Cart Service
**Purpose**: Manage shopping carts

**Technology**: Python FastAPI

**Data Store**: DynamoDB
- Table: `carts`
- Key: `user_id`

**APIs**:
- `GET /cart` - Get user's cart (authenticated)
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{id}` - Update item quantity
- `DELETE /cart/items/{id}` - Remove item
- `DELETE /cart` - Clear cart (internal)

**AWS Services**: ECS/Fargate, DynamoDB, Cognito (auth)

---

### 3. User Service
**Purpose**: Manage user profiles

**Technology**: Python FastAPI

**Data Store**: RDS PostgreSQL
- Table: `users`
- Columns: id, cognito_sub, email, name, phone, address

**APIs**:
- `POST /users/profile` - Create user profile
- `GET /users/profile` - Get current user profile (authenticated)
- `PUT /users/profile` - Update profile
- `GET /users/{id}` - Get user by ID (internal)
- `GET /users/cognito/{sub}` - Get user by Cognito sub (internal)

**AWS Services**: ECS/Fargate, RDS PostgreSQL, Cognito (auth)

---

### 4. Order Service
**Purpose**: Process orders and orchestrate other services

**Technology**: Python FastAPI

**Data Store**: RDS PostgreSQL
- Tables: `orders`, `order_items`

**APIs**:
- `POST /orders` - Create order from cart (authenticated)
- `GET /orders` - Get user's orders
- `GET /orders/{id}` - Get order details

**Order Creation Flow**:
1. Get user details from User Service
2. Get cart items from Cart Service
3. Validate and update inventory via Product Service
4. Create order in database
5. Clear cart via Cart Service
6. Publish order event to SNS

**AWS Services**: ECS/Fargate, RDS PostgreSQL, SNS, Cognito (auth)

---

### 5. Notification Service
**Purpose**: Send order confirmation emails

**Technology**: Python (SQS consumer)

**Data Store**: None (stateless)

**Flow**:
1. Poll SQS queue for messages
2. Parse order event from SNS
3. Send confirmation email via SES
4. Delete message from queue

**AWS Services**: ECS/Fargate, SQS, SES

---

## Data Flow Examples

### Browse Products (Unauthenticated)
```
User → CloudFront → API Gateway → VPC Link → ALB → Product Service → DynamoDB
```

### Add to Cart (Authenticated)
```
User → CloudFront → API Gateway (validates Cognito token) → VPC Link → ALB → Cart Service → DynamoDB
```

### Place Order (Authenticated + Event-Driven)
```
User → API Gateway → ALB → Order Service
                              ├─→ User Service (get email)
                              ├─→ Cart Service (get items, clear cart)
                              ├─→ Product Service (update inventory)
                              ├─→ RDS (create order)
                              └─→ SNS (publish event)
                                   └─→ SQS
                                        └─→ Notification Service
                                             └─→ SES (send email)
```

## AWS Services Used

### Compute
- **ECS/Fargate**: Container orchestration for all 5 microservices
- **Application Load Balancer**: Routes traffic to ECS services

### Storage & Database
- **DynamoDB**: NoSQL database for products and carts (high-velocity data)
- **RDS PostgreSQL**: Relational database for users and orders (transactional data)

### Networking
- **VPC**: Isolated network environment
- **VPC Link**: Connects API Gateway to private ALB
- **Route53**: DNS management
- **CloudFront**: CDN for frontend and API caching

### Frontend
- **S3**: Static website hosting for React app

### Authentication
- **Cognito User Pools**: User authentication and JWT tokens

### Event-Driven
- **SNS**: Pub/sub messaging for order events
- **SQS**: Message queue for reliable notification delivery
- **SES**: Email sending service

### API Management
- **API Gateway (HTTP API)**: Public API endpoint with authentication

## Security Architecture

### Network Security
- Services run in private subnets (no direct internet access)
- ALB is private, only accessible via VPC Link
- Security groups restrict traffic between services
- NAT Gateway for outbound internet access

### Authentication & Authorization
- Cognito manages user authentication
- API Gateway validates JWT tokens
- Services trust internal traffic within VPC
- No service-to-service authentication (trust boundary at VPC level)

### Data Security
- RDS encryption at rest
- DynamoDB encryption at rest
- SSL/TLS for all external communication via CloudFront
- Secrets stored in environment variables (AWS Secrets Manager in production)

## Scalability

### Auto-Scaling
- ECS services can auto-scale based on CPU/memory
- ALB distributes traffic across multiple tasks
- DynamoDB on-demand scaling
- RDS can be scaled vertically

### High Availability
- Multi-AZ deployment for RDS
- ECS tasks distributed across availability zones
- ALB health checks and automatic failover
- DynamoDB multi-AZ replication

## Cost Optimization

### Free Tier Eligible
- DynamoDB: 25GB storage, 25 WCU/RCU
- RDS: 750 hours of t3.micro/t4g.micro
- Cognito: 50,000 MAUs
- SES: 62,000 emails (from EC2/ECS)

### Minimal Configuration
- Fargate: 0.25 vCPU, 0.5GB RAM per task
- RDS: t4g.micro instance
- DynamoDB: On-demand billing
- S3: Standard storage class

### Estimated Costs (Beyond Free Tier)
- **Development/Testing**: ~$2-3/hour
- **24-hour deployment**: ~$50-75
- **Production (minimal)**: ~$100-150/month

## Monitoring & Observability

### CloudWatch
- Service logs from all ECS tasks
- ALB access logs
- API Gateway logs
- Custom metrics for business events

### X-Ray (Optional)
- Distributed tracing across services
- Performance bottleneck identification

## Deployment Strategy

### Local Development
- Docker Compose with LocalStack
- PostgreSQL container
- Nginx as ALB simulator
- Zero AWS cost

### AWS Deployment
1. **Manual** (Tutorial focus): Step-by-step console deployment
2. **Infrastructure as Code**: Terraform for automation

## Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database Clients**: boto3 (DynamoDB), psycopg2 (PostgreSQL)
- **HTTP Client**: httpx (service-to-service)

### Frontend
- **Framework**: React
- **Auth**: AWS Amplify / Cognito SDK
- **HTTP Client**: axios

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: ECS/Fargate
- **IaC**: Terraform (optional)

## Design Patterns

### Microservices
- Single responsibility per service
- Independent deployment and scaling
- Service-to-service communication via HTTP

### Event-Driven Architecture
- Asynchronous processing with SNS/SQS
- Decoupled notification system
- Reliable message delivery

### API Gateway Pattern
- Single entry point for all APIs
- Centralized authentication
- Rate limiting and throttling

### Database per Service
- Each service owns its data
- No direct database sharing
- Data consistency via service APIs

## Learning Objectives

By completing this tutorial, students will learn:

1. **Microservices Architecture**: Design and implement loosely coupled services
2. **AWS Compute**: Deploy containers with ECS/Fargate
3. **AWS Networking**: VPC, subnets, security groups, ALB, VPC Link
4. **AWS Databases**: DynamoDB (NoSQL) and RDS (SQL) use cases
5. **API Management**: API Gateway with authentication
6. **Event-Driven Systems**: SNS/SQS for asynchronous processing
7. **Authentication**: Cognito for user management
8. **Frontend Deployment**: S3 + CloudFront for static hosting
9. **Infrastructure as Code**: Terraform for automation (optional)
10. **Cost Optimization**: Free tier usage and resource sizing

## Next Steps

1. **Local Setup**: Follow `docs/local-setup.md` to run locally
2. **AWS Deployment**: Follow `docs/aws-deployment.md` for manual deployment
3. **IaC**: Use Terraform code for automated deployment (optional)
