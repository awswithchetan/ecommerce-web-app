# AWS Deployment Guide - Ecommerce Application

## Overview
This guide walks you through deploying a production-ready microservices ecommerce application on AWS.

## Learning Objectives
- Deep hands-on experience with core AWS services
- Understanding of cloud architecture patterns
- Best practices for security, scalability, and reliability

## Prerequisites
- AWS Account with admin access
- AWS CLI configured
- Docker installed
- Node.js and npm installed
- Basic understanding of networking and containers

## Architecture Overview

```
User → Route53 → CloudFront → S3 (Frontend)
                      ↓
                 API Gateway (Auth) → VPC Link → ALB
                                                   ↓
                                    ┌──────────────┼──────────────┐
                                    │              │              │
                              ECS Services    ECS Services   ECS Services
                                    │              │              │
                                    └──────────────┼──────────────┘
                                                   ↓
                                    ┌──────────────┴──────────────┐
                                    │                             │
                                  RDS                      SNS → SQS → SES
                              PostgreSQL                  (Notifications)
                            (Users, Orders)
                                    
                              DynamoDB (Global)
                          (Products, Cart - Module 2)
```

## Modules

### [Module 1: Networking Foundation](./module1-networking.md)
**Time:** 30-45 minutes  
**Services:** VPC, Subnets, Internet Gateway, NAT Gateway, Route Tables

Create the network infrastructure:
- VPC with public and private subnets across 2 AZs
- Internet Gateway for public access
- NAT Gateway for private subnet outbound access
- Security groups for network isolation

**Key Concepts:**
- CIDR blocks and IP addressing
- Public vs private subnets
- Routing and gateways
- Network security

---

### [Module 2: Data Layer](./module2-data-layer.md)
**Time:** 20-30 minutes  
**Services:** DynamoDB, RDS PostgreSQL

Set up the databases:
- DynamoDB tables for products and cart (NoSQL, high performance)
- RDS PostgreSQL instance for users and orders (relational, ACID)
- Security groups for database access
- Sample data seeding

**Key Concepts:**
- NoSQL vs SQL databases
- When to use DynamoDB vs RDS
- Database security
- Backup and recovery
- Connection management

---

### [Module 3: Authentication](./module3-authentication.md)
**Time:** 20-30 minutes  
**Services:** Cognito

Configure user authentication:
- Cognito User Pool for user management
- App client for frontend integration
- Hosted UI for authentication flows
- JWT token-based authentication

**Key Concepts:**
- Identity and access management
- OAuth 2.0 flows
- JWT tokens
- Secure authentication

---

### [Module 4: Container Deployment](./module4-container-deployment.md)
**Time:** 60-90 minutes  
**Services:** ECR, ECS Fargate, ALB

Deploy microservices:
- Push Docker images to ECR
- Create ECS cluster with Fargate
- Deploy 4 microservices
- Configure Application Load Balancer
- Set up target groups and health checks

**Key Concepts:**
- Containerization
- Serverless containers (Fargate)
- Load balancing
- Service discovery
- Health checks

---

### [Module 5: API Gateway](./module5-api-gateway.md)
**Time:** 30-45 minutes  
**Services:** API Gateway, VPC Link

Create unified API endpoint:
- HTTP API Gateway
- VPC Link to private ALB
- Cognito authorizer for protected routes
- CORS configuration
- Request/response transformation

**Key Concepts:**
- API management
- Authentication integration
- Private integrations
- API versioning

---

### [Module 6: Event-Driven Architecture](./module6-event-driven.md)
**Time:** 30-45 minutes  
**Services:** SNS, SQS, SES

Implement async notifications:
- SNS topic for order events
- SQS queue for message processing
- Dead letter queue for failed messages
- SES for email notifications
- IAM roles for service permissions

**Key Concepts:**
- Event-driven architecture
- Message queues
- Fan-out pattern
- Decoupling services
- Reliability and retry logic

---

### [Module 7: Frontend Deployment](./module7-frontend-deployment.md)
**Time:** 30-45 minutes  
**Services:** S3, CloudFront

Deploy React frontend:
- S3 bucket for static hosting
- CloudFront distribution for CDN
- Origin Access Identity for security
- Custom error pages for SPA routing
- Cache optimization

**Key Concepts:**
- Static website hosting
- Content Delivery Network (CDN)
- Edge caching
- Global distribution
- HTTPS by default

---

### [Module 8: DNS & SSL](./module8-dns-ssl.md)
**Time:** 30-45 minutes  
**Services:** Route53, ACM

Configure custom domain:
- Route53 hosted zone
- ACM SSL certificate
- DNS validation
- CloudFront custom domain
- Cognito callback URL updates

**Key Concepts:**
- DNS management
- SSL/TLS certificates
- Domain validation
- HTTPS everywhere

---

## Total Time Estimate
**4-6 hours** for complete deployment (excluding domain registration wait time)

## Cost Estimate (Monthly)

| Service | Cost |
|---------|------|
| VPC (NAT Gateway) | $32 |
| DynamoDB (On-Demand) | $1-5 |
| RDS (db.t3.micro) | $15-20 |
| ECS Fargate (4 services) | $115 |
| ALB | $16 |
| API Gateway | $10 |
| SNS/SQS | <$1 |
| SES | <$1 |
| S3 | $5 |
| CloudFront | $5-10 |
| Route53 | $1 |
| **Total** | **~$200-215/month** |

**Cost Optimization Tips:**
- Use Spot instances for non-critical services
- Stop services when not in use (dev/test)
- Use Reserved Instances for production
- Enable auto-scaling to match demand
- Review and delete unused resources

## Deployment Order

**Important:** Follow modules in order as each builds on the previous.

1. **Module 1** - Foundation (VPC must exist first)
2. **Module 2** - Database (needed by services)
3. **Module 3** - Authentication (needed by frontend)
4. **Module 4** - Services (core application)
5. **Module 5** - API Gateway (unified endpoint)
6. **Module 6** - Events (async processing)
7. **Module 7** - Frontend (user interface)
8. **Module 8** - Domain (production ready)

## Quick Start

### Option 1: Manual (Recommended for Learning)
Follow each module's console steps to understand what each service does.

### Option 2: CLI Scripts
Each module includes CLI commands for automation.

### Option 3: Automated
Run the provided scripts (review them first!):

```bash
cd deployment

# Create all infrastructure
./deploy-all.sh

# Cleanup everything
./cleanup-all.sh
```

## Resource Tracking

All resource IDs are saved to `deployment/vpc-resources.txt` for easy reference and cleanup.

## Monitoring and Logging

### CloudWatch Logs
- ECS task logs: `/ecs/<service-name>`
- API Gateway logs: `/aws/apigateway/<api-name>`
- Lambda logs (if added): `/aws/lambda/<function-name>`

### CloudWatch Metrics
- ECS: CPU, Memory utilization
- ALB: Request count, latency, error rates
- RDS: Connections, CPU, storage
- API Gateway: Request count, latency, errors

### View Logs
```bash
# ECS service logs
aws logs tail /ecs/product-service --follow --region ap-south-1

# API Gateway logs
aws logs tail /aws/apigateway/ecommerce-api --follow --region ap-south-1
```

## Troubleshooting

### Common Issues

**1. ECS Tasks Not Starting**
- Check CloudWatch logs for errors
- Verify security groups allow traffic
- Ensure task role has required permissions
- Check environment variables

**2. ALB Health Checks Failing**
- Verify health check path exists
- Check security group rules
- Ensure service is listening on correct port
- Review task logs

**3. API Gateway 403 Errors**
- Check Cognito authorizer configuration
- Verify JWT token is valid
- Ensure correct audience in token
- Check CORS configuration

**4. Database Connection Errors**
- Verify security group allows ECS → RDS
- Check database endpoint and credentials
- Ensure RDS is in available state
- Test connectivity from ECS task

**5. CloudFront Not Serving Updated Content**
- Create invalidation: `aws cloudfront create-invalidation --distribution-id <id> --paths "/*"`
- Check S3 bucket has latest files
- Verify CloudFront origin settings

## Security Best Practices

✅ **Implemented:**
- Private subnets for services and database
- Security groups with least privilege
- Encrypted data at rest (RDS, S3)
- HTTPS everywhere (CloudFront, API Gateway)
- IAM roles with minimal permissions
- Cognito for authentication

🔒 **Additional Recommendations:**
- Enable AWS WAF on CloudFront/ALB
- Set up AWS GuardDuty for threat detection
- Enable VPC Flow Logs
- Use AWS Secrets Manager for credentials
- Enable MFA for AWS account
- Regular security audits with AWS Security Hub

## Backup and Disaster Recovery

### RDS Backups
- Automated daily backups (7-day retention)
- Manual snapshots before major changes
- Cross-region replication for DR

### Application State
- ECS task definitions versioned
- Infrastructure as Code (save all CLI commands)
- S3 versioning for frontend

### Recovery Procedures
1. Database: Restore from RDS snapshot
2. Services: Redeploy from ECR images
3. Frontend: Redeploy from S3 versioned objects

## Scaling Considerations

### Horizontal Scaling
- ECS Service Auto Scaling (target tracking)
- ALB distributes traffic across tasks
- RDS Read Replicas for read-heavy workloads

### Vertical Scaling
- Increase ECS task CPU/memory
- Upgrade RDS instance class
- Adjust ALB capacity

### Auto Scaling Configuration
```bash
# Example: Scale ECS service based on CPU
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/ecommerce-cluster/product-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/ecommerce-cluster/product-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    TargetValue=70.0,PredefinedMetricSpecification={PredefinedMetricType=ECSServiceAverageCPUUtilization}
```

## CI/CD Pipeline (Future Enhancement)

### Using GitHub Actions
```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push Docker images
      - name: Update ECS services
      - name: Deploy frontend to S3
      - name: Invalidate CloudFront
```

### Using AWS CodePipeline
1. Source: GitHub/CodeCommit
2. Build: CodeBuild (Docker images)
3. Deploy: ECS rolling update

## Testing

### Local Testing
```bash
cd local-deployment
docker-compose up
```

### Integration Testing
- Test each API endpoint
- Verify authentication flow
- Test order creation and email notification
- Load testing with tools like Apache JMeter

### Smoke Tests After Deployment
```bash
# Test products endpoint
curl https://yourdomain.com/api/products

# Test health checks
curl https://yourdomain.com/api/users/health
curl https://yourdomain.com/api/orders/health
```

## Cleanup

### Complete Cleanup
```bash
cd deployment
./cleanup-all.sh
```

### Manual Cleanup Order
1. Module 8: Delete Route53 records, ACM certificate
2. Module 7: Delete CloudFront, S3 bucket
3. Module 6: Delete SNS, SQS, IAM roles
4. Module 5: Delete API Gateway, VPC Link
5. Module 4: Delete ECS services, cluster, ALB, ECR
6. Module 3: Delete Cognito User Pool
7. Module 2: Delete RDS instance
8. Module 1: Delete VPC resources

**Important:** Some resources take time to delete (CloudFront: 15-20 min, RDS: 5-10 min)

## Additional Resources

### AWS Documentation
- [VPC User Guide](https://docs.aws.amazon.com/vpc/)
- [ECS Developer Guide](https://docs.aws.amazon.com/ecs/)
- [API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/)
- [Cognito Developer Guide](https://docs.aws.amazon.com/cognito/)

### Best Practices
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)

## Support

### Issues and Questions
- Check CloudWatch Logs first
- Review module documentation
- AWS Support (if you have a support plan)
- AWS Forums and Stack Overflow

## Congratulations! 🎉

You've learned how to:
- Design and implement cloud architecture
- Deploy microservices on AWS
- Configure networking and security
- Set up authentication and authorization
- Implement event-driven patterns
- Deploy and distribute frontend applications
- Configure custom domains with SSL

These skills are directly applicable to real-world production systems!
