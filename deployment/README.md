# AWS Deployment Guide - Ecommerce Application

## Overview
This guide walks you through deploying a production-ready microservices ecommerce application on AWS using modern cloud architecture patterns.

## Architecture Overview
<img width="800" height="450" alt="project-architecture" src="https://github.com/user-attachments/assets/d3512e16-6224-44a0-9148-d3b2d511b33d" />

## Deployment Modules

Complete these modules in order:

### [Module 0: Prerequisites](./module00-prerequisites.md)
**Time:** 10-15 minutes  
**Setup:** AWS CLI, Docker, Git
- Install required tools
- Configure AWS credentials
- Clone repository

### [Module 1: Networking Foundation](./module01-networking.md)
**Time:** 30-45 minutes  
**Services:** VPC, Subnets, Internet Gateway, NAT Gateway, Route Tables
- Create VPC with public and private subnets across 2 AZs
- Set up Internet Gateway and NAT Gateway for connectivity

### [Module 2: Authentication](./module02-authentication.md)
**Time:** 30-45 minutes  
**Services:** Cognito User Pools
- User registration and authentication
- JWT token management

### [Module 3: Frontend Infrastructure](./module03-frontend-infrastructure.md)
**Time:** 15-20 minutes  
**Services:** S3, CloudFront
- S3 bucket for static website hosting
- CloudFront distribution for CDN and HTTPS

### [Module 4: Data Layer](./module04-data-layer.md)
**Time:** 45-60 minutes  
**Services:** DynamoDB, RDS PostgreSQL, S3
- DynamoDB tables for products and cart data
- RDS PostgreSQL for users and orders
- S3 bucket for product images

### [Module 5: Container Deployment](./module05-backend-deployment.md)
**Time:** 60-90 minutes  
**Services:** ECR, ECS, Fargate, Internal ALB, Parameter Store
- Build and push Docker images
- Deploy microservices on ECS Fargate with Parameter Store configuration
- Configure internal load balancing

### [Module 6: API Gateway](./module06-api-gateway.md)
**Time:** 30-45 minutes  
**Services:** API Gateway, VPC Link
- Create unified API endpoint with VPC Link
- Integrate Cognito authentication
- Route requests to internal ALB

### [Module 7: Frontend-Backend Integration](./module07-frontend-backend-integration.md)
**Time:** 15-20 minutes  
**Services:** S3, CloudFront
- Configure `aws-config.js` with Cognito and API Gateway values
- Build and deploy React application to S3
- Invalidate CloudFront cache

### [Module 8: Event-Driven Architecture](./module08-notification.md)
**Time:** 30-45 minutes  
**Services:** SNS, SQS
- Direct SNS email notifications
- SQS logging for order events

### [Module 9: DNS & SSL](./module09-custom-domain-and-ssl.md)
**Time:** 30-45 minutes (Optional)  
**Services:** Route53, Certificate Manager
- Custom domain setup
- SSL certificate configuration

### [Module 10: Search](./module10-search.md)
**Time:** 45-60 minutes  
**Services:** OpenSearch, Lambda, DynamoDB Streams
- Full-text product search with OpenSearch
- Lambda search handler behind internal ALB
- DynamoDB Stream → Lambda indexer for real-time sync

### [Module 11: Cleanup](./module11-cleanup.md)
**Time:** 15-20 minutes  
- Remove all AWS resources
- Avoid ongoing charges

## Important Notes

### Region Consistency
- **Primary Region:** ap-south-1 (Mumbai)
- **Certificate Manager:** us-east-1 (required for CloudFront)
- Keep all other resources in ap-south-1

## Cost Estimate (24-hour deployment)

| Service | Daily Cost |
|---------|------------|
| VPC (NAT Gateway) | $1.07 |
| DynamoDB (On-Demand) | $0.03-0.17 |
| RDS (db.t3.micro) | $0.50-0.67 |
| ECS Fargate (4 services) | $3.83 |
| Internal ALB | $0.53 |
| API Gateway + VPC Link | $0.93 |
| SNS/SQS | <$0.03 |
| S3 + CloudFront (Frontend) | $0.33-0.50 |
| S3 + CloudFront (Images) | $0.05-0.10 |
| Route53 | $0.03 |
| **Total per day** | **~$7.30-7.86** |

**If completed in 4 hours:** ~$1.20-1.30  
**Monthly production cost:** ~$218-233
