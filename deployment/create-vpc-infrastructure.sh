#!/bin/bash

# Module 1: Create VPC Infrastructure
# Region: ap-south-1 (Mumbai)

set -e

echo "=== Creating VPC Infrastructure ==="

# 1. Create VPC
echo "Creating VPC..."
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ecommerce-vpc}]' \
  --region ap-south-1 \
  --query 'Vpc.VpcId' \
  --output text)
echo "VPC Created: $VPC_ID"

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-hostnames \
  --region ap-south-1

# 2. Create Subnets
echo "Creating subnets..."

# Public Subnet 1 (ap-south-1a)
PUBLIC_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ap-south-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=ecommerce-public-subnet-1}]' \
  --region ap-south-1 \
  --query 'Subnet.SubnetId' \
  --output text)
echo "Public Subnet 1: $PUBLIC_SUBNET_1"

# Public Subnet 2 (ap-south-1b)
PUBLIC_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone ap-south-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=ecommerce-public-subnet-2}]' \
  --region ap-south-1 \
  --query 'Subnet.SubnetId' \
  --output text)
echo "Public Subnet 2: $PUBLIC_SUBNET_2"

# Private Subnet 1 (ap-south-1a)
PRIVATE_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone ap-south-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=ecommerce-private-subnet-1}]' \
  --region ap-south-1 \
  --query 'Subnet.SubnetId' \
  --output text)
echo "Private Subnet 1: $PRIVATE_SUBNET_1"

# Private Subnet 2 (ap-south-1b)
PRIVATE_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.12.0/24 \
  --availability-zone ap-south-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=ecommerce-private-subnet-2}]' \
  --region ap-south-1 \
  --query 'Subnet.SubnetId' \
  --output text)
echo "Private Subnet 2: $PRIVATE_SUBNET_2"

# 3. Create and attach Internet Gateway
echo "Creating Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=ecommerce-igw}]' \
  --region ap-south-1 \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)
echo "Internet Gateway: $IGW_ID"

aws ec2 attach-internet-gateway \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID \
  --region ap-south-1

# 4. Allocate Elastic IP for NAT Gateway
echo "Allocating Elastic IP..."
EIP_ALLOC_ID=$(aws ec2 allocate-address \
  --domain vpc \
  --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=ecommerce-nat-eip}]' \
  --region ap-south-1 \
  --query 'AllocationId' \
  --output text)
echo "Elastic IP Allocation ID: $EIP_ALLOC_ID"

# 5. Create NAT Gateway in Public Subnet 1
echo "Creating NAT Gateway (this takes a few minutes)..."
NAT_GW_ID=$(aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_1 \
  --allocation-id $EIP_ALLOC_ID \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=ecommerce-nat-gw}]' \
  --region ap-south-1 \
  --query 'NatGateway.NatGatewayId' \
  --output text)
echo "NAT Gateway: $NAT_GW_ID"

# Wait for NAT Gateway to be available
echo "Waiting for NAT Gateway to be available..."
aws ec2 wait nat-gateway-available \
  --nat-gateway-ids $NAT_GW_ID \
  --region ap-south-1
echo "NAT Gateway is available"

# 6. Create Route Tables
echo "Creating route tables..."

# Public Route Table
PUBLIC_RT_ID=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=ecommerce-public-rt}]' \
  --region ap-south-1 \
  --query 'RouteTable.RouteTableId' \
  --output text)
echo "Public Route Table: $PUBLIC_RT_ID"

# Private Route Table
PRIVATE_RT_ID=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=ecommerce-private-rt}]' \
  --region ap-south-1 \
  --query 'RouteTable.RouteTableId' \
  --output text)
echo "Private Route Table: $PRIVATE_RT_ID"

# 7. Create Routes
echo "Creating routes..."

# Public route to Internet Gateway
aws ec2 create-route \
  --route-table-id $PUBLIC_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID \
  --region ap-south-1

# Private route to NAT Gateway
aws ec2 create-route \
  --route-table-id $PRIVATE_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $NAT_GW_ID \
  --region ap-south-1

# 8. Associate Route Tables with Subnets
echo "Associating route tables with subnets..."

aws ec2 associate-route-table \
  --subnet-id $PUBLIC_SUBNET_1 \
  --route-table-id $PUBLIC_RT_ID \
  --region ap-south-1

aws ec2 associate-route-table \
  --subnet-id $PUBLIC_SUBNET_2 \
  --route-table-id $PUBLIC_RT_ID \
  --region ap-south-1

aws ec2 associate-route-table \
  --subnet-id $PRIVATE_SUBNET_1 \
  --route-table-id $PRIVATE_RT_ID \
  --region ap-south-1

aws ec2 associate-route-table \
  --subnet-id $PRIVATE_SUBNET_2 \
  --route-table-id $PRIVATE_RT_ID \
  --region ap-south-1

# 9. Enable auto-assign public IP for public subnets
echo "Enabling auto-assign public IP for public subnets..."
aws ec2 modify-subnet-attribute \
  --subnet-id $PUBLIC_SUBNET_1 \
  --map-public-ip-on-launch \
  --region ap-south-1

aws ec2 modify-subnet-attribute \
  --subnet-id $PUBLIC_SUBNET_2 \
  --map-public-ip-on-launch \
  --region ap-south-1

# 10. Save resource IDs to file
echo "Saving resource IDs..."
cat > vpc-resources.txt <<EOF
VPC_ID=$VPC_ID
PUBLIC_SUBNET_1=$PUBLIC_SUBNET_1
PUBLIC_SUBNET_2=$PUBLIC_SUBNET_2
PRIVATE_SUBNET_1=$PRIVATE_SUBNET_1
PRIVATE_SUBNET_2=$PRIVATE_SUBNET_2
IGW_ID=$IGW_ID
NAT_GW_ID=$NAT_GW_ID
EIP_ALLOC_ID=$EIP_ALLOC_ID
PUBLIC_RT_ID=$PUBLIC_RT_ID
PRIVATE_RT_ID=$PRIVATE_RT_ID
EOF

echo ""
echo "=== VPC Infrastructure Created Successfully ==="
echo ""
cat vpc-resources.txt
echo ""
echo "Resource IDs saved to: vpc-resources.txt"
