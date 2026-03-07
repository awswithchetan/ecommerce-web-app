# Module 2: Data Layer

## Overview
Set up databases for the ecommerce application:
- **DynamoDB** for high-performance NoSQL data (products, cart)
- **RDS PostgreSQL** for relational data (users, orders)
- Security groups for database access

## Architecture
```
DynamoDB (Global, Serverless)
├── Table: products
│   ├── Partition Key: product_id (String)
│   └── Attributes: name, description, price, stock, image_url
└── Table: cart
    ├── Partition Key: user_id (String)
    ├── Sort Key: product_id (String)
    └── Attributes: quantity, price, added_at

Private Subnets
├── RDS PostgreSQL (Multi-AZ)
│   ├── Database: ecommerce_db
│   ├── Tables: users, orders, order_items
│   └── Port: 5432
└── Security Group: rds-sg
    └── Inbound: Port 5432 from ECS tasks
```

## Why This Design?

**DynamoDB for Products & Cart:**
- High read/write throughput for product catalog
- Low latency for cart operations
- Automatic scaling
- No schema migrations needed
- Pay per request (cost-effective for variable traffic)

**RDS PostgreSQL for Users & Orders:**
- ACID transactions for order processing
- Complex queries and joins
- Referential integrity
- Consistent data for financial records

## Resources to Create

### 1. DynamoDB Tables

**Products Table:**
- Table name: ecommerce-products
- Partition key: product_id (String)
- Billing mode: On-demand (pay per request)
- Encryption: Enabled

**Cart Table:**
- Table name: ecommerce-cart
- Partition key: user_id (String)
- Sort key: product_id (String)
- Billing mode: On-demand
- TTL: enabled on `expires_at` attribute (optional)
- Encryption: Enabled

### 2. DB Subnet Group
- Name: ecommerce-db-subnet-group
- Subnets: Both private subnets (from Module 1)

### 3. Security Group for RDS
- Name: ecommerce-rds-sg
- VPC: ecommerce-vpc
- Inbound Rules:
  - PostgreSQL (5432) from ECS security group (will create in Module 4)
  - For now: PostgreSQL (5432) from VPC CIDR (10.0.0.0/16)

### 4. RDS PostgreSQL Instance
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

### 5. IAM Policy for DynamoDB Access
- Allow ECS tasks to read/write DynamoDB tables

## Console Steps

### Step 1: Create DynamoDB Tables

**Products Table:**
1. Go to DynamoDB Console → Tables → Create table
2. Table name: `ecommerce-products`
3. Partition key: `product_id` (String)
4. Table settings: Customize settings
5. Table class: DynamoDB Standard
6. Capacity mode: On-demand
7. Encryption: Amazon DynamoDB owned key (or use AWS managed key)
8. Create table

**Cart Table:**
1. DynamoDB Console → Tables → Create table
2. Table name: `ecommerce-cart`
3. Partition key: `user_id` (String)
4. Sort key: `product_id` (String)
5. Table settings: Customize settings
6. Capacity mode: On-demand
7. Encryption: Amazon DynamoDB owned key
8. Create table

**Optional - Enable TTL for Cart:**
1. Go to cart table → Additional settings → Time to Live (TTL)
2. Enable TTL
3. TTL attribute: `expires_at`
4. This auto-deletes old cart items

### Step 2: Create DB Subnet Group
1. Go to RDS Console → Subnet groups
2. Click "Create DB subnet group"
3. Name: `ecommerce-db-subnet-group`
4. Description: "Subnet group for ecommerce RDS"
5. VPC: Select `ecommerce-vpc`
6. Add subnets:
   - Select both availability zones (ap-south-1a, ap-south-1b)
   - Select both private subnets
7. Create

### Step 2: Create DB Subnet Group

1. Go to RDS Console → Subnet groups
2. Click "Create DB subnet group"
3. Name: `ecommerce-db-subnet-group`
4. Description: "Subnet group for ecommerce RDS"
5. VPC: Select `ecommerce-vpc`
6. Add subnets:
   - Select both availability zones (ap-south-1a, ap-south-1b)
   - Select both private subnets
7. Create

### Step 3: Create Security Group for RDS
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

### Step 3: Create Security Group for RDS

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

### Step 4: Create RDS Instance
### Step 4: Create RDS Instance

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

### Step 5: Seed DynamoDB Tables with Sample Data

**Products Table:**
1. Go to DynamoDB Console → Tables → ecommerce-products
2. Actions → Create item
3. Add sample products (or use CLI below)

**Sample Product:**
```json
{
  "product_id": "prod-001",
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "stock": 50,
  "image_url": "https://example.com/laptop.jpg",
  "category": "Electronics"
}
```

## CLI Commands

### Create DynamoDB Tables

**Products Table:**
```bash
aws dynamodb create-table \
  --table-name ecommerce-products \
  --attribute-definitions \
    AttributeName=product_id,AttributeType=S \
  --key-schema \
    AttributeName=product_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --sse-specification Enabled=true \
  --region ap-south-1

echo "PRODUCTS_TABLE=ecommerce-products" >> deployment/vpc-resources.txt
```

**Cart Table:**
```bash
aws dynamodb create-table \
  --table-name ecommerce-cart \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=product_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=product_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --sse-specification Enabled=true \
  --region ap-south-1

echo "CART_TABLE=ecommerce-cart" >> deployment/vpc-resources.txt
```

**Enable TTL on Cart Table (Optional):**
```bash
aws dynamodb update-time-to-live \
  --table-name ecommerce-cart \
  --time-to-live-specification "Enabled=true,AttributeName=expires_at" \
  --region ap-south-1
```

### Seed Products Table with Sample Data

**Option 1: Use provided data file (Recommended)**
```bash
cd data
./load-products.sh ecommerce-products ap-south-1
```

This loads 20 sample products from `data/products.json`.

**Option 2: Manual CLI commands**
```bash
# Product 1
aws dynamodb put-item \
  --table-name ecommerce-products \
  --item '{
    "product_id": {"S": "prod-001"},
    "name": {"S": "Wireless Bluetooth Headphones"},
    "description": {"S": "Premium noise-cancelling over-ear headphones"},
    "price": {"N": "89.99"},
    "stock": {"N": "150"},
    "image_url": {"S": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"},
    "category": {"S": "Electronics"}
  }' \
  --region ap-south-1
```

See `data/products.json` for all 20 products.

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

### RDS PostgreSQL Schema
Once RDS is created, the schema will be automatically created by each microservice on startup:

**Users Table** (user-service):
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    cognito_sub VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Orders Table** (order-service):
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    user_email VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
```

### DynamoDB Schema

**Products Table:**
- Partition Key: `product_id` (String)
- Attributes: name, description, price, stock, image_url, category

**Cart Table:**
- Partition Key: `user_id` (String)
- Sort Key: `product_id` (String)
- Attributes: quantity, price, added_at, expires_at (optional TTL)

### Connection String Format
**RDS PostgreSQL:**
```
postgresql://postgres:YourPassword@<DB_ENDPOINT>:5432/ecommerce_db
```

**DynamoDB:**
- Use AWS SDK with IAM role credentials
- No connection string needed

## Verification

### Check DynamoDB Tables
```bash
# List tables
aws dynamodb list-tables --region ap-south-1

# Describe products table
aws dynamodb describe-table \
  --table-name ecommerce-products \
  --region ap-south-1 \
  --query 'Table.[TableName,TableStatus,ItemCount]' \
  --output table

# Scan products (get all items)
aws dynamodb scan \
  --table-name ecommerce-products \
  --region ap-south-1

# Get specific product
aws dynamodb get-item \
  --table-name ecommerce-products \
  --key '{"product_id": {"S": "prod-001"}}' \
  --region ap-south-1
```

### Check RDS Status
```bash
aws rds describe-db-instances \
  --db-instance-identifier ecommerce-db \
  --region ap-south-1 \
  --query 'DBInstances[0].[DBInstanceStatus,Endpoint.Address,Endpoint.Port]' \
  --output table
```

## Cost Considerations
- **DynamoDB On-Demand:**
  - First 25 GB storage: Free
  - Write: $1.25 per million requests
  - Read: $0.25 per million requests
  - For low traffic: ~$1-5/month
- **RDS db.t3.micro:** ~$15-20/month (free tier eligible for 12 months)
- **RDS Storage (20GB gp3):** ~$2.50/month
- **RDS Backup storage:** First 20GB free
- **Total:** ~$18-28/month (or ~$3-8/month with free tier)

## Cleanup Commands
```bash
# Delete DynamoDB tables
aws dynamodb delete-table \
  --table-name ecommerce-products \
  --region ap-south-1

aws dynamodb delete-table \
  --table-name ecommerce-cart \
  --region ap-south-1

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

## Service Configuration

### Product Service (uses DynamoDB)
Environment variables:
```
DYNAMODB_TABLE=ecommerce-products
AWS_REGION=ap-south-1
ENVIRONMENT=production
```

### Cart Service (uses DynamoDB)
Environment variables:
```
DYNAMODB_TABLE=ecommerce-cart
AWS_REGION=ap-south-1
ENVIRONMENT=production
```

### User Service (uses RDS)
Environment variables:
```
DATABASE_URL=postgresql://postgres:<password>@<db-endpoint>:5432/ecommerce_db
ENVIRONMENT=production
```

### Order Service (uses RDS)
Environment variables:
```
DATABASE_URL=postgresql://postgres:<password>@<db-endpoint>:5432/ecommerce_db
USER_SERVICE_URL=http://user-service:8003
CART_SERVICE_URL=http://cart-service:8002
PRODUCT_SERVICE_URL=http://product-service:8001
ENVIRONMENT=production
```

## Next Steps
After completing this module:
- ✅ DynamoDB tables created for products and cart
- ✅ RDS PostgreSQL instance running in private subnets for users and orders
- ✅ Security group configured for database access
- ✅ Sample products loaded
- Ready for Module 3: Authentication (Cognito)
