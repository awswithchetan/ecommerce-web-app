# eCommerce Frontend

React-based frontend for the eCommerce application.

## Features

- **Product Listing** - Browse all available products
- **Shopping Cart** - Add/remove items, view cart
- **Checkout** - Place orders
- **Order History** - View past orders

## Local Development

### Prerequisites
- Node.js 18+
- Backend services running (see main README)

### Setup

```bash
cd frontend/react-app
npm install
npm start
```

The app will open at http://localhost:3000

### Environment Variables

Create `.env` file:
```
REACT_APP_API_URL=http://localhost:8080/api
```

## Components

- **Products** - Product catalog with add to cart
- **Cart** - Shopping cart management
- **Orders** - Order history
- **Navbar** - Navigation

## API Integration

Uses mock user ID for local testing. In production, integrate with AWS Cognito for authentication.

## Build for Production

```bash
npm run build
```

Outputs to `build/` directory, ready for S3 deployment.

## Docker

Build and run with Docker:

```bash
docker build -t ecommerce-frontend .
docker run -p 3000:80 ecommerce-frontend
```

## AWS Deployment

1. Build the app: `npm run build`
2. Upload `build/` contents to S3 bucket
3. Configure CloudFront distribution
4. Update `REACT_APP_API_URL` to point to API Gateway

## Notes

- Currently uses mock authentication (X-User-Id header)
- For production, implement Cognito authentication
- Product images use placeholders
