#!/bin/bash

# Quick test script for local deployment
# Run this after docker-compose up

echo "========================================="
echo "Testing eCommerce Application"
echo "========================================="
echo ""

BASE_URL="http://localhost:8080/api"
USER_ID="test-user-123"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local headers=$5
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" $headers "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method $headers -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "$body"
    fi
    echo ""
}

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Test 1: List products
test_endpoint "List Products" "GET" "$BASE_URL/products"

# Test 2: Get specific product
test_endpoint "Get Product" "GET" "$BASE_URL/products/prod-001"

# Test 3: Create user
test_endpoint "Create User" "POST" "$BASE_URL/users/profile" \
    '{"cognito_sub":"'$USER_ID'","email":"test@example.com","name":"Test User","phone":"+1234567890","address":"123 Test St"}'

# Test 4: Get user profile
test_endpoint "Get User Profile" "GET" "$BASE_URL/users/profile" "" "-H 'X-User-Id: $USER_ID'"

# Test 5: Add item to cart
test_endpoint "Add Laptop to Cart" "POST" "$BASE_URL/cart/items" \
    '{"product_id":"prod-001","quantity":1,"price":999.99}' \
    "-H 'X-User-Id: $USER_ID'"

# Test 6: Add another item to cart
test_endpoint "Add Mouse to Cart" "POST" "$BASE_URL/cart/items" \
    '{"product_id":"prod-002","quantity":2,"price":29.99}' \
    "-H 'X-User-Id: $USER_ID'"

# Test 7: View cart
test_endpoint "View Cart" "GET" "$BASE_URL/cart" "" "-H 'X-User-Id: $USER_ID'"

# Test 8: Place order
test_endpoint "Place Order" "POST" "$BASE_URL/orders" '{}' "-H 'X-User-Id: $USER_ID'"

# Test 9: View orders
test_endpoint "View Orders" "GET" "$BASE_URL/orders" "" "-H 'X-User-Id: $USER_ID'"

# Test 10: Check cart is empty
test_endpoint "Check Cart Cleared" "GET" "$BASE_URL/cart" "" "-H 'X-User-Id: $USER_ID'"

echo "========================================="
echo "Testing Complete!"
echo "========================================="
echo ""
echo "Check notification-service logs for email:"
echo "  docker-compose logs notification-service"
echo ""
echo "Check DynamoDB tables:"
echo "  awslocal dynamodb scan --table-name products"
echo ""
echo "Check PostgreSQL:"
echo "  docker-compose exec postgres psql -U postgres -d ecommerce_db -c 'SELECT * FROM orders;'"
