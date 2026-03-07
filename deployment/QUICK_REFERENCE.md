# AWS Deployment Modules - Quick Reference

## Module Overview

| Module | Services | Time | Difficulty | Cost/Month |
|--------|----------|------|------------|------------|
| 1. Networking | VPC, Subnets, IGW, NAT, Route Tables | 30-45 min | ⭐⭐ | $32 |
| 2. Data Layer | DynamoDB, RDS PostgreSQL | 20-30 min | ⭐⭐ | $16-25 |
| 3. Authentication | Cognito | 20-30 min | ⭐⭐ | Free |
| 4. Containers | ECR, ECS, ALB | 60-90 min | ⭐⭐⭐⭐ | $131 |
| 5. API Gateway | API Gateway, VPC Link | 30-45 min | ⭐⭐⭐ | $10 |
| 6. Events | SNS, SQS, SES | 30-45 min | ⭐⭐⭐ | <$1 |
| 7. Frontend | S3, CloudFront | 30-45 min | ⭐⭐ | $10 |
| 8. DNS & SSL | Route53, ACM | 30-45 min | ⭐⭐ | $1 |

**Total:** 4-6 hours | ~$200-215/month

## Files Created

```
deployment/
├── README.md                          # Master guide
├── QUICK_REFERENCE.md                 # This file
├── module1-networking.md              # VPC setup
├── module2-data-layer.md              # RDS setup
├── module3-authentication.md          # Cognito setup
├── module4-container-deployment.md    # ECS setup
├── module5-api-gateway.md             # API Gateway setup
├── module6-event-driven.md            # SNS/SQS/SES setup
├── module7-frontend-deployment.md     # S3/CloudFront setup
├── module8-dns-ssl.md                 # Route53/ACM setup
├── create-vpc-infrastructure.sh       # Module 1 automation
├── cleanup-vpc-infrastructure.sh      # Module 1 cleanup
└── vpc-resources.txt                  # Resource IDs (generated)
```

## Quick Commands

### Check AWS Configuration
```bash
aws configure list
aws sts get-caller-identity
```

### Start Deployment
```bash
cd deployment
# Follow modules 1-8 in order
```

### Track Resources
```bash
# All resource IDs saved here
cat deployment/vpc-resources.txt
```

### View Logs
```bash
# ECS service logs
aws logs tail /ecs/product-service --follow --region ap-south-1

# API Gateway logs
aws logs tail /aws/apigateway/ecommerce-api --follow --region ap-south-1
```

### Common Operations
```bash
# Update ECS service
aws ecs update-service \
  --cluster ecommerce-cluster \
  --service product-service \
  --force-new-deployment \
  --region ap-south-1

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <id> \
  --paths "/*"

# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier ecommerce-db \
  --region ap-south-1 \
  --query 'DBInstances[0].DBInstanceStatus'
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │ Route53 │ (Module 8)
                    └────┬────┘
                         │
                  ┌──────▼──────┐
                  │ CloudFront  │ (Module 7)
                  └──────┬──────┘
                         │
            ┌────────────┴────────────┐
            │                         │
       ┌────▼────┐              ┌────▼────────┐
       │   S3    │              │ API Gateway │ (Module 5)
       │Frontend │              │   (JWT)     │
       └─────────┘              └────┬────────┘
                                     │
                              ┌──────▼──────┐
                              │  VPC Link   │
                              └──────┬──────┘
                                     │
┌────────────────────────────────────┼────────────────────────┐
│                    VPC (Module 1)  │                        │
│                              ┌─────▼─────┐                  │
│                              │    ALB    │ (Module 4)       │
│                              └─────┬─────┘                  │
│                                    │                        │
│  ┌─────────────────────────────────┼──────────────┐        │
│  │ Private Subnets                 │              │        │
│  │                                 │              │        │
│  │  ┌──────────────────────────────┼────────┐     │        │
│  │  │ ECS Cluster (Module 4)       │        │     │        │
│  │  │                              │        │     │        │
│  │  │  ┌────────┐  ┌────────┐  ┌──▼─────┐  │     │        │
│  │  │  │Product │  │  Cart  │  │ Order  │  │     │        │
│  │  │  │Service │  │Service │  │Service │  │     │        │
│  │  │  └────┬───┘  └────┬───┘  └───┬────┘  │     │        │
│  │  │       │           │          │       │     │        │
│  │  │       └───────────┼──────────┘       │     │        │
│  │  │                   │                  │     │        │
│  │  │              ┌────▼────┐             │     │        │
│  │  │              │   RDS   │ (Module 2) │     │        │
│  │  │              │  (PG)   │             │     │        │
│  │  │              └─────────┘             │     │        │
│  │  └────────────────────────────────────────────┘        │
│  │                                                         │
│  │  ┌──────────────────────────────────────┐              │
│  │  │ Event Processing (Module 6)          │              │
│  │  │                                      │              │
│  │  │  Order Service → SNS → SQS → SES    │              │
│  │  └──────────────────────────────────────┘              │
│  └─────────────────────────────────────────────────────────┘
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Public Subnets                                      │  │
│  │  ┌──────────┐         ┌──────────┐                 │  │
│  │  │   ALB    │         │   NAT    │                 │  │
│  │  │          │         │ Gateway  │                 │  │
│  │  └──────────┘         └──────────┘                 │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘

External: Cognito (Module 3) - User Authentication
```

## Service Dependencies

```
Module 1 (VPC)
    ↓
Module 2 (RDS) ← depends on VPC
    ↓
Module 3 (Cognito) ← independent
    ↓
Module 4 (ECS) ← depends on VPC, RDS
    ↓
Module 5 (API Gateway) ← depends on ECS, Cognito
    ↓
Module 6 (SNS/SQS) ← depends on ECS
    ↓
Module 7 (Frontend) ← depends on API Gateway, Cognito
    ↓
Module 8 (DNS) ← depends on Frontend
```

## Key Concepts by Module

### Module 1: Networking
- CIDR blocks and subnetting
- Public vs private subnets
- Internet Gateway vs NAT Gateway
- Route tables and routing
- Security groups

### Module 2: Data Layer
- NoSQL vs SQL databases
- DynamoDB partition and sort keys
- DynamoDB on-demand pricing
- RDS managed databases
- Multi-AZ deployments
- Automated backups
- Security group rules
- Connection strings

### Module 3: Authentication
- User pools and identity
- OAuth 2.0 flows
- JWT tokens
- Hosted UI
- App clients

### Module 4: Containers
- Docker containerization
- ECS Fargate (serverless)
- Task definitions
- Service discovery
- Load balancing
- Health checks

### Module 5: API Gateway
- HTTP APIs
- VPC Link (private integration)
- JWT authorizers
- CORS configuration
- Request routing

### Module 6: Events
- Pub/Sub pattern
- Message queues
- Dead letter queues
- Fan-out architecture
- Email notifications

### Module 7: Frontend
- Static website hosting
- CDN and edge caching
- Origin Access Identity
- SPA routing
- Cache invalidation

### Module 8: DNS & SSL
- DNS management
- SSL/TLS certificates
- DNS validation
- Alias records
- Custom domains

## Troubleshooting Quick Reference

| Issue | Check | Solution |
|-------|-------|----------|
| ECS tasks not starting | CloudWatch Logs | Check env vars, IAM roles |
| ALB health checks fail | Security groups | Allow ALB → ECS traffic |
| API Gateway 403 | Cognito token | Verify JWT, authorizer config |
| Database connection | Security groups | Allow ECS → RDS traffic |
| CloudFront stale content | Cache | Create invalidation |
| DNS not resolving | Route53 records | Check A record, nameservers |
| SSL certificate pending | ACM validation | Add CNAME to Route53 |

## Cost Optimization Tips

1. **Stop services when not in use** (dev/test)
   ```bash
   aws ecs update-service --cluster ecommerce-cluster \
     --service product-service --desired-count 0
   ```

2. **Use Spot instances** for non-critical workloads

3. **Enable auto-scaling** to match demand

4. **Delete unused resources** regularly

5. **Use Reserved Instances** for production (1-3 year commitment)

6. **Monitor with Cost Explorer** and set billing alerts

## Security Checklist

- [ ] All services in private subnets (except ALB)
- [ ] Security groups follow least privilege
- [ ] RDS encryption enabled
- [ ] S3 bucket not public
- [ ] HTTPS everywhere
- [ ] IAM roles with minimal permissions
- [ ] Cognito MFA enabled (production)
- [ ] CloudWatch logging enabled
- [ ] Regular security audits
- [ ] Secrets in Secrets Manager (not env vars)

## Next Steps After Deployment

1. **Set up CI/CD pipeline**
   - GitHub Actions or CodePipeline
   - Automated testing
   - Blue/green deployments

2. **Add monitoring**
   - CloudWatch dashboards
   - X-Ray tracing
   - Custom metrics

3. **Implement auto-scaling**
   - ECS service auto-scaling
   - RDS read replicas
   - DynamoDB on-demand

4. **Enhance security**
   - AWS WAF
   - GuardDuty
   - Security Hub
   - VPC Flow Logs

5. **Disaster recovery**
   - Cross-region replication
   - Automated backups
   - Recovery procedures

## Learning Resources

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [AWS Workshops](https://workshops.aws/)
- [AWS Skill Builder](https://skillbuilder.aws/)

## Support

- AWS Documentation: https://docs.aws.amazon.com/
- AWS Forums: https://forums.aws.amazon.com/
- Stack Overflow: Tag `amazon-web-services`
- AWS Support (if you have a plan)
