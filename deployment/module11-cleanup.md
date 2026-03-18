# Module 11: Cleanup

## Overview
Clean up all AWS resources created during this tutorial to avoid ongoing charges.

## Cleanup Order

Delete resources in reverse order of creation to avoid dependency issues:

### 1. DNS & SSL (Module 9)
- Route53 DNS records (A records, CNAME records)
- ACM SSL certificate
- Route53 Public hosted zone

### 2. Search (Module 10)
- OpenSearch domain
- Lambda functions (search-handler, dynamodb-indexer)
- Lambda target group (ALB)
- DynamoDB Stream (disable on products table)
- IAM role (Lambda execution role)

### 3. Notification (Module 8)
- SNS subscriptions (email, SQS)
- SQS queue
- SNS topic

### 3. Frontend-Backend Integration (Module 7)
- S3 bucket contents (frontend files)

### 4. API Gateway (Module 6)
- API Gateway HTTP API
- VPC Link
- JWT Authorizer

### 5. Container Deployment (Module 5)
- ECS services
- ECS cluster
- ECS task definitions
- ECR repositories
- Application Load Balancer
- Target groups
- IAM role (ECS task role)
- Security group (ECS tasks)

### 6. Data Layer (Module 4)
- RDS database instance
- DB subnet group
- Security group (RDS)
- DynamoDB tables (products, cart)
- Parameter Store parameters

### 7. Frontend Infrastructure (Module 3)
- CloudFront distribution (frontend)
- S3 bucket (frontend)

### 8. Authentication (Module 2)
- Cognito User Pool
- Cognito App Client

### 9. Networking (Module 1)
- NAT Gateway
- Elastic IP
- Internet Gateway
- Route tables (public, private ECS, private database)
- Subnets (public, private ECS, private database)
- Security groups (ALB)
- VPC

**Important:** Always delete resources in the correct order to avoid dependency errors and ensure complete cleanup.
