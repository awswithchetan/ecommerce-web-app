#!/bin/bash

# Cleanup VPC Infrastructure
# This will delete all resources created by create-vpc-infrastructure.sh

set -e

# Load resource IDs
source vpc-resources.txt

echo "=== Cleaning up VPC Infrastructure ==="

# 1. Delete NAT Gateway
echo "Deleting NAT Gateway..."
aws ec2 delete-nat-gateway \
  --nat-gateway-id $NAT_GW_ID \
  --region ap-south-1

echo "Waiting for NAT Gateway to be deleted..."
aws ec2 wait nat-gateway-deleted \
  --nat-gateway-ids $NAT_GW_ID \
  --region ap-south-1

# 2. Release Elastic IP
echo "Releasing Elastic IP..."
aws ec2 release-address \
  --allocation-id $EIP_ALLOC_ID \
  --region ap-south-1

# 3. Disassociate subnets from route tables
echo "Disassociating subnets from route tables..."
for assoc_id in $(aws ec2 describe-route-tables --route-table-ids $PUBLIC_RT_ID $PRIVATE_RT_ID --region ap-south-1 --query 'RouteTables[].Associations[?SubnetId!=`null`].RouteTableAssociationId' --output text); do
  aws ec2 disassociate-route-table --association-id $assoc_id --region ap-south-1 || true
done

# 4. Delete routes
echo "Deleting routes..."
aws ec2 delete-route \
  --route-table-id $PUBLIC_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --region ap-south-1 || true

aws ec2 delete-route \
  --route-table-id $PRIVATE_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --region ap-south-1 || true

# 5. Delete route tables
echo "Deleting route tables..."
aws ec2 delete-route-table \
  --route-table-id $PUBLIC_RT_ID \
  --region ap-south-1

aws ec2 delete-route-table \
  --route-table-id $PRIVATE_RT_ID \
  --region ap-south-1

# 5. Detach and delete Internet Gateway
echo "Detaching and deleting Internet Gateway..."
aws ec2 detach-internet-gateway \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID \
  --region ap-south-1

aws ec2 delete-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --region ap-south-1

# 6. Delete subnets
echo "Deleting subnets..."
aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_1 --region ap-south-1
aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_2 --region ap-south-1
aws ec2 delete-subnet --subnet-id $PRIVATE_SUBNET_1 --region ap-south-1
aws ec2 delete-subnet --subnet-id $PRIVATE_SUBNET_2 --region ap-south-1

# 7. Delete VPC
echo "Deleting VPC..."
aws ec2 delete-vpc --vpc-id $VPC_ID --region ap-south-1

echo ""
echo "=== Cleanup Complete ==="
