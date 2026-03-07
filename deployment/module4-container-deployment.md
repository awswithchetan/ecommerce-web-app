# Module 4: Container Deployment with ECS

## Overview
Deploy microservices as Docker containers on Amazon ECS (Elastic Container Service) with Fargate.

## Architecture
```
ECS Cluster
├── Service: product-service (Port 8001)
├── Service: cart-service (Port 8002)
├── Service: user-service (Port 8003)
├── Service: order-service (Port 8004)
└── Service: notification-service

Application Load Balancer (Public)
├── Target Group: product-tg → product-service
├── Target Group: cart-tg → cart-service
├── Target Group: user-tg → user-service
└── Target Group: order-tg → order-service
```

## Resources to Create

### 1. ECR Repositories (for Docker images)
- product-service
- cart-service
- user-service
- order-service
- notification-service

### 2. Security Groups
- ALB Security Group (allow HTTP/HTTPS from internet)
- ECS Security Group (allow traffic from ALB)

### 3. Application Load Balancer
- Name: ecommerce-alb
- Scheme: Internet-facing
- Subnets: Both public subnets
- Target groups for each service

### 4. ECS Cluster
- Name: ecommerce-cluster
- Infrastructure: AWS Fargate

### 5. Task Definitions
- One for each microservice
- CPU: 256 (.25 vCPU)
- Memory: 512 MB
- Environment variables for DB connection

### 6. ECS Services
- One for each microservice
- Desired count: 1
- Launch type: Fargate
- Subnets: Private subnets
- Load balancer: Connect to target groups

## Console Steps

### Step 1: Create ECR Repositories

1. Go to ECR Console → Repositories
2. Click "Create repository"
3. For each service:
   - Repository name: `product-service`, `cart-service`, `user-service`, `order-service`, `notification-service`
   - Image tag mutability: Mutable
   - Scan on push: Enable
   - Create repository

### Step 2: Build and Push Docker Images

```bash
# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# For each service
cd services/product-service
docker build -t product-service .
docker tag product-service:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/product-service:latest
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/product-service:latest

# Repeat for cart-service, user-service, order-service, notification-service
```

### Step 3: Create Security Groups

**ALB Security Group:**
1. VPC Console → Security Groups → Create
2. Name: `ecommerce-alb-sg`
3. VPC: ecommerce-vpc
4. Inbound rules:
   - HTTP (80) from 0.0.0.0/0
   - HTTPS (443) from 0.0.0.0/0
5. Create

**ECS Security Group:**
1. Name: `ecommerce-ecs-sg`
2. VPC: ecommerce-vpc
3. Inbound rules:
   - Custom TCP 8001-8004 from ALB security group
   - PostgreSQL (5432) - for RDS access (update RDS SG too)
4. Create

**Update RDS Security Group:**
1. Go to RDS security group
2. Add inbound rule:
   - PostgreSQL (5432) from ECS security group

### Step 4: Create Application Load Balancer

1. EC2 Console → Load Balancers → Create
2. Load balancer type: Application Load Balancer
3. Name: `ecommerce-alb`
4. Scheme: Internet-facing
5. IP address type: IPv4
6. Network mapping:
   - VPC: ecommerce-vpc
   - Subnets: Select both public subnets
7. Security groups: Select `ecommerce-alb-sg`
8. Listeners: HTTP (80) - we'll add target groups next
9. Create load balancer

### Step 5: Create Target Groups

For each service, create a target group:

**Product Service Target Group:**
1. EC2 Console → Target Groups → Create
2. Target type: IP addresses
3. Name: `product-tg`
4. Protocol: HTTP, Port: 8001
5. VPC: ecommerce-vpc
6. Health check:
   - Path: /health
   - Interval: 30 seconds
   - Timeout: 5 seconds
   - Healthy threshold: 2
   - Unhealthy threshold: 3
7. Create (don't register targets yet)

**Repeat for:**
- `cart-tg` (Port 8002, Path /health)
- `user-tg` (Port 8003, Path /health)
- `order-tg` (Port 8004, Path /health)

### Step 6: Configure ALB Listener Rules

1. Go to Load Balancer → Listeners tab
2. Click on HTTP:80 listener
3. Add rules:
   - Path `/api/products*` → Forward to `product-tg`
   - Path `/api/cart*` → Forward to `cart-tg`
   - Path `/api/users*` → Forward to `user-tg`
   - Path `/api/orders*` → Forward to `order-tg`
4. Default action: Return fixed response (404)

### Step 7: Create ECS Cluster

1. ECS Console → Clusters → Create cluster
2. Cluster name: `ecommerce-cluster`
3. Infrastructure: AWS Fargate (serverless)
4. Create

### Step 8: Create Task Execution Role

1. IAM Console → Roles → Create role
2. Trusted entity: ECS Task
3. Permissions:
   - AmazonECSTaskExecutionRolePolicy
   - CloudWatchLogsFullAccess (for logging)
4. Role name: `ecsTaskExecutionRole`
5. Create

### Step 9: Create Task Definitions

**Product Service Task Definition:**
1. ECS Console → Task Definitions → Create new task definition
2. Task definition family: `product-service-task`
3. Launch type: AWS Fargate
4. Operating system: Linux
5. Task size:
   - CPU: .25 vCPU (256)
   - Memory: 0.5 GB (512)
6. Task execution role: ecsTaskExecutionRole
7. Container:
   - Name: product-service
   - Image URI: `<account-id>.dkr.ecr.ap-south-1.amazonaws.com/product-service:latest`
   - Port mappings: 8001 (TCP)
   - Environment variables:
     - DATABASE_URL: `postgresql://postgres:<password>@<db-endpoint>:5432/ecommerce_db`
     - ENVIRONMENT: `production`
   - Log configuration:
     - Log driver: awslogs
     - Log group: /ecs/product-service (auto-create)
8. Create

**Repeat for other services** with appropriate ports and environment variables.

### Step 10: Create ECS Services

**Product Service:**
1. ECS Console → Clusters → ecommerce-cluster → Services → Create
2. Launch type: Fargate
3. Task definition: product-service-task (latest)
4. Service name: `product-service`
5. Number of tasks: 1
6. Deployment type: Rolling update
7. Networking:
   - VPC: ecommerce-vpc
   - Subnets: Select both private subnets
   - Security group: ecommerce-ecs-sg
   - Auto-assign public IP: Disabled
8. Load balancing:
   - Load balancer type: Application Load Balancer
   - Load balancer: ecommerce-alb
   - Container to load balance: product-service:8001
   - Target group: product-tg
9. Service auto scaling: None (for now)
10. Create service

**Repeat for other services** with their respective task definitions and target groups.

## CLI Commands

### Create ECR Repositories
```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

for service in product-service cart-service user-service order-service notification-service; do
  aws ecr create-repository \
    --repository-name $service \
    --image-scanning-configuration scanOnPush=true \
    --region ap-south-1
done

echo "ACCOUNT_ID=$ACCOUNT_ID" >> deployment/vpc-resources.txt
```

### Build and Push Images
```bash
# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com

# Build and push each service
for service in product-service cart-service user-service order-service notification-service; do
  cd services/$service
  docker build -t $service .
  docker tag $service:latest $ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/$service:latest
  docker push $ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/$service:latest
  cd ../..
done
```

### Create Security Groups
```bash
source deployment/vpc-resources.txt

# ALB Security Group
ALB_SG_ID=$(aws ec2 create-security-group \
  --group-name ecommerce-alb-sg \
  --description "Security group for ALB" \
  --vpc-id $VPC_ID \
  --region ap-south-1 \
  --query 'GroupId' \
  --output text)

aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region ap-south-1

# ECS Security Group
ECS_SG_ID=$(aws ec2 create-security-group \
  --group-name ecommerce-ecs-sg \
  --description "Security group for ECS tasks" \
  --vpc-id $VPC_ID \
  --region ap-south-1 \
  --query 'GroupId' \
  --output text)

aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG_ID \
  --protocol tcp \
  --port 8001-8004 \
  --source-group $ALB_SG_ID \
  --region ap-south-1

# Update RDS SG to allow ECS
aws ec2 authorize-security-group-ingress \
  --group-id $RDS_SG_ID \
  --protocol tcp \
  --port 5432 \
  --source-group $ECS_SG_ID \
  --region ap-south-1

echo "ALB_SG_ID=$ALB_SG_ID" >> deployment/vpc-resources.txt
echo "ECS_SG_ID=$ECS_SG_ID" >> deployment/vpc-resources.txt
```

### Create Application Load Balancer
```bash
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name ecommerce-alb \
  --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
  --security-groups $ALB_SG_ID \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --region ap-south-1 \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

ALB_DNS=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns $ALB_ARN \
  --region ap-south-1 \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

echo "ALB_ARN=$ALB_ARN" >> deployment/vpc-resources.txt
echo "ALB_DNS=$ALB_DNS" >> deployment/vpc-resources.txt
echo "Load Balancer DNS: $ALB_DNS"
```

### Create Target Groups
```bash
# Product Target Group
PRODUCT_TG_ARN=$(aws elbv2 create-target-group \
  --name product-tg \
  --protocol HTTP \
  --port 8001 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --region ap-south-1 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Cart Target Group
CART_TG_ARN=$(aws elbv2 create-target-group \
  --name cart-tg \
  --protocol HTTP \
  --port 8002 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-path /health \
  --region ap-south-1 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# User Target Group
USER_TG_ARN=$(aws elbv2 create-target-group \
  --name user-tg \
  --protocol HTTP \
  --port 8003 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-path /health \
  --region ap-south-1 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Order Target Group
ORDER_TG_ARN=$(aws elbv2 create-target-group \
  --name order-tg \
  --protocol HTTP \
  --port 8004 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-path /health \
  --region ap-south-1 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

echo "PRODUCT_TG_ARN=$PRODUCT_TG_ARN" >> deployment/vpc-resources.txt
echo "CART_TG_ARN=$CART_TG_ARN" >> deployment/vpc-resources.txt
echo "USER_TG_ARN=$USER_TG_ARN" >> deployment/vpc-resources.txt
echo "ORDER_TG_ARN=$ORDER_TG_ARN" >> deployment/vpc-resources.txt
```

### Create ALB Listener with Rules
```bash
# Create listener
LISTENER_ARN=$(aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=fixed-response,FixedResponseConfig="{StatusCode=404,ContentType=text/plain,MessageBody=Not Found}" \
  --region ap-south-1 \
  --query 'Listeners[0].ListenerArn' \
  --output text)

# Add rules for each service
aws elbv2 create-rule \
  --listener-arn $LISTENER_ARN \
  --priority 1 \
  --conditions Field=path-pattern,Values='/api/products*' \
  --actions Type=forward,TargetGroupArn=$PRODUCT_TG_ARN \
  --region ap-south-1

aws elbv2 create-rule \
  --listener-arn $LISTENER_ARN \
  --priority 2 \
  --conditions Field=path-pattern,Values='/api/cart*' \
  --actions Type=forward,TargetGroupArn=$CART_TG_ARN \
  --region ap-south-1

aws elbv2 create-rule \
  --listener-arn $LISTENER_ARN \
  --priority 3 \
  --conditions Field=path-pattern,Values='/api/users*' \
  --actions Type=forward,TargetGroupArn=$USER_TG_ARN \
  --region ap-south-1

aws elbv2 create-rule \
  --listener-arn $LISTENER_ARN \
  --priority 4 \
  --conditions Field=path-pattern,Values='/api/orders*' \
  --actions Type=forward,TargetGroupArn=$ORDER_TG_ARN \
  --region ap-south-1

echo "LISTENER_ARN=$LISTENER_ARN" >> deployment/vpc-resources.txt
```

### Create ECS Cluster
```bash
CLUSTER_ARN=$(aws ecs create-cluster \
  --cluster-name ecommerce-cluster \
  --region ap-south-1 \
  --query 'cluster.clusterArn' \
  --output text)

echo "CLUSTER_ARN=$CLUSTER_ARN" >> deployment/vpc-resources.txt
```

### Create Task Execution Role
```bash
# Create trust policy
cat > /tmp/ecs-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
TASK_EXEC_ROLE_ARN=$(aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document file:///tmp/ecs-trust-policy.json \
  --query 'Role.Arn' \
  --output text)

# Attach policies
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

echo "TASK_EXEC_ROLE_ARN=$TASK_EXEC_ROLE_ARN" >> deployment/vpc-resources.txt
```

### Create Task Definitions

See `deployment/task-definitions/` directory for JSON files.

```bash
# Register task definitions
aws ecs register-task-definition \
  --cli-input-json file://deployment/task-definitions/product-service.json \
  --region ap-south-1

# Repeat for other services
```

### Create ECS Services

```bash
# Product Service
aws ecs create-service \
  --cluster ecommerce-cluster \
  --service-name product-service \
  --task-definition product-service-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2],securityGroups=[$ECS_SG_ID],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=$PRODUCT_TG_ARN,containerName=product-service,containerPort=8001" \
  --region ap-south-1

# Repeat for other services
```

## Verification

### Check Service Status
```bash
aws ecs describe-services \
  --cluster ecommerce-cluster \
  --services product-service cart-service user-service order-service \
  --region ap-south-1 \
  --query 'services[].[serviceName,status,runningCount,desiredCount]' \
  --output table
```

### Test Endpoints
```bash
ALB_DNS=$(cat deployment/vpc-resources.txt | grep ALB_DNS | cut -d'=' -f2)

curl http://$ALB_DNS/api/products
curl http://$ALB_DNS/api/users/health
```

## Cost Considerations
- Fargate: ~$0.04/hour per task (256 CPU, 512 MB)
- 4 services × 24 hours × 30 days = ~$115/month
- ALB: ~$16/month + data transfer
- ECR: $0.10/GB/month for storage

## Next Steps
After completing this module:
- ✅ Microservices running on ECS Fargate
- ✅ ALB routing traffic to services
- ✅ Services can access RDS
- Ready for Module 5: API Gateway
