# Module 2: Data Layer

## Overview
Set up databases for the ecommerce application:
- RDS PostgreSQL for relational data (users, orders, products, cart)
- Security groups for database access

## Architecture
```
Private Subnets
├── RDS PostgreSQL (Multi-AZ)
│   ├── Database: ecommerce_db
│   └── Port: 5432
└── Security Group: rds-sg
    └── Inbound: Port 5432 from ECS tasks
```

## Resources to Create

### 1. DB Subnet Group
- Name: ecommerce-db-subnet-group
- Subnets: Both private subnets (from Module 1)

### 2. Security Group for RDS
- Name: ecommerce-rds-sg
- VPC: ecommerce-vpc
- Inbound Rules:
  - PostgreSQL (5432) from ECS security group (will create in Module 4)
  - For now: PostgreSQL (5432) from VPC CIDR (10.0.0.0/16)

### 3. RDS PostgreSQL Instance
- Engine: PostgreSQL 15
- Instance class: db.t3.micro (Free tier eligible)
- Storage: 20 GB gp3
- Multi-AZ: No (for cost savings in dev)
- Database name: ecommerce_db
- Master username: postgres
- Master password: (choose a strong password)
- Subnet group: ecommerce-db-subnet-group
- Security group: ecommerce-rds-sg
- Backup retention: 7 days
- Public access: No

## Console Steps

### Step 1: Create DB Subnet Group
1. Go to RDS Console → Subnet groups
2. Click "Create DB subnet group"
3. Name: `ecommerce-db-subnet-group`
4. Description: "Subnet group for ecommerce RDS"
5. VPC: Select `ecommerce-vpc`
6. Add subnets:
   - Select both availability zones (ap-south-1a, ap-south-1b)
   - Select both private subnets
7. Create

### Step 2: Create Security Group for RDS
1. Go to VPC Console → Security Groups
2. Click "Create security group"
3. Name: `ecommerce-rds-sg`
4. Description: "Security group for RDS PostgreSQL"
5. VPC: Select `ecommerce-vpc`
6. Inbound rules:
   - Type: PostgreSQL
   - Port: 5432
   - Source: Custom - 10.0.0.0/16 (VPC CIDR)
   - Description: "Allow PostgreSQL from VPC"
7. Outbound rules: Keep default (all traffic)
8. Create

### Step 3: Create RDS Instance
1. Go to RDS Console → Databases
2. Click "Create database"
3. Choose creation method: Standard create
4. Engine options:
   - Engine type: PostgreSQL
   - Version: PostgreSQL 15.x (latest)
5. Templates: Free tier (or Dev/Test)
6. Settings:
   - DB instance identifier: `ecommerce-db`
   - Master username: `postgres`
   - Master password: (create strong password - save it!)
   - Confirm password
7. Instance configuration:
   - DB instance class: Burstable classes - db.t3.micro
8. Storage:
   - Storage type: gp3
   - Allocated storage: 20 GiB
   - Storage autoscaling: Disable (for cost control)
9. Connectivity:
   - VPC: `ecommerce-vpc`
   - DB subnet group: `ecommerce-db-subnet-group`
   - Public access: No
   - VPC security group: Choose existing - `ecommerce-rds-sg`
   - Availability Zone: No preference
10. Database authentication: Password authentication
11. Additional configuration:
    - Initial database name: `ecommerce_db`
    - Backup retention period: 7 days
    - Enable encryption: Yes (default KMS key)
12. Create database (takes 5-10 minutes)

## CLI Commands

### Create DB Subnet Group
```bash
# Load VPC resource IDs
source deployment/vpc-resources.txt

aws rds create-db-subnet-group \
  --db-subnet-group-name ecommerce-db-subnet-group \
  --db-subnet-group-description "Subnet group for ecommerce RDS" \
  --subnet-ids $PRIVATE_SUBNET_1 $PRIVATE_SUBNET_2 \
  --tags Key=Name,Value=ecommerce-db-subnet-group \
  --region ap-south-1
```

### Create Security Group for RDS
```bash
RDS_SG_ID=$(aws ec2 create-security-group \
  --group-name ecommerce-rds-sg \
  --description "Security group for RDS PostgreSQL" \
  --vpc-id $VPC_ID \
  --region ap-south-1 \
  --query 'GroupId' \
  --output text)

aws ec2 authorize-security-group-ingress \
  --group-id $RDS_SG_ID \
  --protocol tcp \
  --port 5432 \
  --cidr 10.0.0.0/16 \
  --region ap-south-1

echo "RDS_SG_ID=$RDS_SG_ID" >> deployment/vpc-resources.txt
```

### Create RDS Instance
```bash
aws rds create-db-instance \
  --db-instance-identifier ecommerce-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.5 \
  --master-username postgres \
  --master-user-password 'YourStrongPassword123!' \
  --allocated-storage 20 \
  --storage-type gp3 \
  --db-subnet-group-name ecommerce-db-subnet-group \
  --vpc-security-group-ids $RDS_SG_ID \
  --db-name ecommerce_db \
  --backup-retention-period 7 \
  --no-publicly-accessible \
  --storage-encrypted \
  --region ap-south-1

# Wait for DB to be available (takes 5-10 minutes)
aws rds wait db-instance-available \
  --db-instance-identifier ecommerce-db \
  --region ap-south-1

# Get DB endpoint
DB_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier ecommerce-db \
  --region ap-south-1 \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

echo "DB_ENDPOINT=$DB_ENDPOINT" >> deployment/vpc-resources.txt
echo "Database endpoint: $DB_ENDPOINT"
```

## Initialize Database Schema

Once RDS is created, you'll need to connect and create tables. This will be done from an EC2 instance or ECS task in the private subnet.

### Connection String Format
```
postgresql://postgres:YourPassword@<DB_ENDPOINT>:5432/ecommerce_db
```

### Schema Initialization
The database schema will be automatically created by each microservice on startup (see service code).

## Verification

### Check RDS Status
```bash
aws rds describe-db-instances \
  --db-instance-identifier ecommerce-db \
  --region ap-south-1 \
  --query 'DBInstances[0].[DBInstanceStatus,Endpoint.Address,Endpoint.Port]' \
  --output table
```

## Cost Considerations
- db.t3.micro: ~$15-20/month (free tier eligible for 12 months)
- Storage (20GB gp3): ~$2.50/month
- Backup storage: First 20GB free

## Cleanup Commands
```bash
# Delete RDS instance (skip final snapshot for dev)
aws rds delete-db-instance \
  --db-instance-identifier ecommerce-db \
  --skip-final-snapshot \
  --region ap-south-1

# Wait for deletion
aws rds wait db-instance-deleted \
  --db-instance-identifier ecommerce-db \
  --region ap-south-1

# Delete subnet group
aws rds delete-db-subnet-group \
  --db-subnet-group-name ecommerce-db-subnet-group \
  --region ap-south-1

# Delete security group
aws ec2 delete-security-group \
  --group-id $RDS_SG_ID \
  --region ap-south-1
```

## Next Steps
After completing this module:
- ✅ RDS PostgreSQL instance running in private subnets
- ✅ Security group configured for database access
- Ready for Module 3: Authentication (Cognito)
