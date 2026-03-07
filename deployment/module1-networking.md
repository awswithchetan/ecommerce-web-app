# Module 1: Networking Foundation

## Overview
Create VPC infrastructure with public and private subnets across 2 availability zones.

## Architecture
```
VPC (10.0.0.0/16)
├── Public Subnet 1 (10.0.1.0/24) - ap-south-1a
├── Public Subnet 2 (10.0.2.0/24) - ap-south-1b
├── Private Subnet 1 (10.0.11.0/24) - ap-south-1a
├── Private Subnet 2 (10.0.12.0/24) - ap-south-1b
├── Internet Gateway
├── NAT Gateway (in Public Subnet 1)
└── Route Tables
```

## Resources Created
1. VPC
2. 2 Public Subnets
3. 2 Private Subnets
4. Internet Gateway
5. NAT Gateway
6. Elastic IP (for NAT Gateway)
7. Public Route Table
8. Private Route Table
9. Security Groups (ALB, ECS, RDS)

## Console Steps (for reference)

### 1. Create VPC
- VPC Dashboard → Create VPC
- Name: ecommerce-vpc
- IPv4 CIDR: 10.0.0.0/16
- Tenancy: Default

### 2. Create Subnets
Create 4 subnets with the CIDR blocks above

### 3. Create Internet Gateway
- Attach to VPC

### 4. Create NAT Gateway
- Place in Public Subnet 1
- Allocate Elastic IP

### 5. Configure Route Tables
- Public: 0.0.0.0/0 → Internet Gateway
- Private: 0.0.0.0/0 → NAT Gateway

## CLI Commands
See `create-vpc-infrastructure.sh` script
