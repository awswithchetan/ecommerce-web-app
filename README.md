# AWS eCommerce Tutorial

A hands-on tutorial for building a production-grade eCommerce application on AWS using microservices architecture.

## Architecture

### Services
- **Product Service** - Product catalog management (DynamoDB)
- **Cart Service** - Shopping cart operations (DynamoDB)
- **User Service** - User profile management (RDS PostgreSQL)
- **Order Service** - Order processing and orchestration (RDS PostgreSQL)
- **Notification Service** - Async email notifications (SQS → SES)

### AWS Services Used
- **Frontend**: S3 + CloudFront + Route53
- **API Layer**: API Gateway (HTTP API) + VPC Link
- **Compute**: ECS/Fargate + Application Load Balancer
- **Auth**: Cognito User Pools
- **Data**: DynamoDB + RDS PostgreSQL
- **Events**: SNS + SQS + SES

## Repository Structure

```
ecommerce-aws-tutorial/
├── services/
│   ├── product-service/       # Python FastAPI
│   ├── cart-service/          # Python FastAPI
│   ├── user-service/          # Python FastAPI
│   ├── order-service/         # Python FastAPI
│   └── notification-service/  # Python FastAPI
├── frontend/
│   └── react-app/             # React application
├── local-deployment/
│   ├── docker-compose.yml     # Local stack with LocalStack
│   ├── localstack-init/       # Init scripts for LocalStack
│   └── nginx.conf             # ALB simulator
├── aws-deployment/
│   ├── manual-steps/          # Step-by-step AWS deployment guide
│   └── terraform/             # IaC (optional advanced module)
├── docs/
│   ├── architecture.md
│   ├── local-setup.md
│   └── aws-deployment.md
└── README.md
```

## Getting Started

### Quick Start (Recommended)

**Want to get up and running fast?** Follow the [QUICKSTART.md](QUICKSTART.md) guide:

1. Create AWS Cognito User Pool (~5 minutes)
2. Configure credentials in `aws-config.js`
3. Start backend with Docker Compose
4. Start frontend with npm
5. Test complete authentication flow

**Total time: ~15 minutes**

### Detailed Setup

For step-by-step instructions, see:
- [Local Setup Guide](docs/local-setup.md) - Detailed local development setup
- [Cognito Setup Guide](docs/COGNITO_SETUP_GUIDE.md) - AWS Cognito configuration
- [Testing Guide](TESTING_GUIDE.md) - How to test the application

## Learning Path

1. **Part 1**: Local deployment and testing (understand the application)
2. **Part 2**: Manual AWS deployment (learn AWS services hands-on)
3. **Part 3**: Infrastructure as Code with Terraform (optional)

## Cost Estimates

- Local development: $0
- AWS deployment (4-hour session): ~$10-15
- AWS deployment (24 hours): ~$50-75

## License

MIT
