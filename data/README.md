# Product Data

This directory contains sample product data for the ecommerce application.

## Files

- **products.json** - 20 sample products with details
- **load-products.sh** - Script to load products into DynamoDB

## Product Categories

- Electronics (14 products)
- Accessories (5 products)
- Furniture (1 product)

## Product Data Structure

Each product contains:
- `product_id` - Unique identifier (e.g., "prod-001")
- `name` - Product name
- `description` - Product description
- `price` - Price in USD (decimal)
- `stock` - Available quantity (integer)
- `category` - Product category
- `image_url` - Product image URL (from Unsplash)

## Loading Products into DynamoDB

### Prerequisites
- AWS CLI configured
- DynamoDB table created (see Module 2)
- `jq` installed for JSON processing

### Usage

```bash
# Load into default table (ecommerce-products) in ap-south-1
cd data
./load-products.sh

# Specify custom table name and region
./load-products.sh my-products-table us-east-1
```

### Verify Loading

```bash
# Check item count
aws dynamodb scan \
  --table-name ecommerce-products \
  --region ap-south-1 \
  --select COUNT

# Get all products
aws dynamodb scan \
  --table-name ecommerce-products \
  --region ap-south-1

# Get specific product
aws dynamodb get-item \
  --table-name ecommerce-products \
  --key '{"product_id": {"S": "prod-001"}}' \
  --region ap-south-1
```

## Product Images

All product images are sourced from [Unsplash](https://unsplash.com), a free stock photo service. Images are served via CDN and are optimized for web use.

## Customization

To add more products:
1. Edit `products.json`
2. Follow the same JSON structure
3. Use sequential product IDs (prod-021, prod-022, etc.)
4. Run the load script

## Sample Products

1. Wireless Bluetooth Headphones - $89.99
2. Smart Watch Series 5 - $299.99
3. Mechanical Gaming Keyboard - $129.99
4. 4K Webcam - $79.99
5. Wireless Gaming Mouse - $59.99
6. USB-C Hub 7-in-1 - $39.99
7. Portable SSD 1TB - $119.99
8. Laptop Stand Aluminum - $34.99
9. Wireless Charging Pad - $24.99
10. Bluetooth Speaker Portable - $49.99
11. HD Monitor 27-inch - $189.99
12. Desk Lamp LED - $29.99
13. Laptop Backpack - $44.99
14. Microphone USB Condenser - $69.99
15. Cable Management Kit - $19.99
16. Ergonomic Office Chair - $249.99
17. Ring Light 10-inch - $39.99
18. Power Bank 20000mAh - $34.99
19. HDMI Cable 6ft - $14.99
20. Webcam Privacy Cover - $9.99

**Total Inventory Value:** ~$1,800
**Average Price:** $75.99
**Total Stock:** 4,675 units
