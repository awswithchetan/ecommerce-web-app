#!/bin/bash

# Load products into DynamoDB
# Usage: ./load-products.sh [table-name] [region]

TABLE_NAME=${1:-ecommerce-products}
REGION=${2:-ap-south-1}

echo "Loading products into DynamoDB table: $TABLE_NAME"
echo "Region: $REGION"
echo ""

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    echo "Install with: sudo apt-get install jq (Ubuntu/Debian) or brew install jq (Mac)"
    exit 1
fi

# Read products from JSON file
PRODUCTS_FILE="$(dirname "$0")/products.json"

if [ ! -f "$PRODUCTS_FILE" ]; then
    echo "Error: products.json not found at $PRODUCTS_FILE"
    exit 1
fi

# Count total products
TOTAL=$(jq length "$PRODUCTS_FILE")
echo "Found $TOTAL products to load"
echo ""

# Load each product
COUNTER=0
jq -c '.[]' "$PRODUCTS_FILE" | while read -r product; do
    COUNTER=$((COUNTER + 1))
    
    # Extract product details for display
    PRODUCT_ID=$(echo "$product" | jq -r '.product_id')
    NAME=$(echo "$product" | jq -r '.name')
    
    echo "[$COUNTER/$TOTAL] Loading: $NAME ($PRODUCT_ID)"
    
    # Convert JSON to DynamoDB format
    ITEM=$(echo "$product" | jq '{
        product_id: {S: .product_id},
        name: {S: .name},
        description: {S: .description},
        price: {N: (.price | tostring)},
        stock: {N: (.stock | tostring)},
        category: {S: .category},
        image_url: {S: .image_url}
    }')
    
    # Put item into DynamoDB
    aws dynamodb put-item \
        --table-name "$TABLE_NAME" \
        --item "$ITEM" \
        --region "$REGION" \
        2>&1 | grep -v "^$"
    
    if [ $? -eq 0 ]; then
        echo "  ✓ Success"
    else
        echo "  ✗ Failed"
    fi
    echo ""
done

echo "Loading complete!"
echo ""
echo "Verify with:"
echo "aws dynamodb scan --table-name $TABLE_NAME --region $REGION --query 'Count'"
