# eCommerce AWS Tutorial - Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Node.js 18+ installed
- AWS Account (free tier)

## Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd ecommerce-aws-tutorial
```

## Step 2: Create AWS Cognito User Pool

### 2.1 Go to AWS Console
1. Log into AWS Console: https://console.aws.amazon.com
2. **Select Region**: ap-south-1 (Mumbai) - top right corner
3. Search for "Cognito" and click on it
4. Click **"Create user pool"**

### 2.2 Configure User Pool

**Step 1 - Authentication providers:**
- Select: ☑ Email
- Click Next

**Step 2 - Security requirements:**
- Password policy: Cognito defaults
- MFA: No MFA
- Click Next

**Step 3 - Sign-up experience:**
- Self-service sign-up: ☑ Enabled
- Required attributes: ☑ email, ☑ name
- Click Next

**Step 4 - Message delivery:**
- Email provider: Send email with Cognito (easier for testing)
- Click Next

**Step 5 - Integrate your app:**
- User pool name: `ecommerce-user-pool`
- App type: **Single-page application (SPA)**
- App client name: `ecommerce-web-client`
- Callback URL: `http://localhost:3000`
- Authentication flows: 
  - ☑ ALLOW_USER_SRP_AUTH
  - ☑ ALLOW_REFRESH_TOKEN_AUTH
- Click Next

**Step 6 - Review and create:**
- Click **Create user pool**

### 2.3 Get Your Credentials

After creation:
1. Copy **User Pool ID** (looks like: `ap-south-1_xxxxxxxxx`)
2. Go to "App integration" tab
3. Click on your app client
4. Copy **Client ID** (long string)

## Step 3: Configure the Application

Edit the file: `frontend/react-app/src/aws-config.js`

Replace the placeholder values:

```javascript
const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: 'YOUR_USER_POOL_ID_HERE',      // Replace this
      userPoolClientId: 'YOUR_CLIENT_ID_HERE',    // Replace this
      loginWith: {
        email: true,
      },
    }
  }
};

export default awsConfig;
```

## Step 4: Start the Application

### 4.1 Start Backend Services

```bash
cd local-deployment
docker-compose up --build
```

Wait for all services to start (~2 minutes). You should see:
- ✅ LocalStack running
- ✅ PostgreSQL running
- ✅ All 5 microservices running
- ✅ Nginx running

### 4.2 Configure Frontend API URL

Edit `frontend/react-app/.env`:

**For local development:**
```
REACT_APP_API_URL=http://localhost:8080/api
```

**For EC2 deployment:**
```
REACT_APP_API_URL=http://<EC2-PUBLIC-IP>:8080/api
```

### 4.3 Start Frontend

Open a new terminal:

```bash
cd frontend/react-app
npm install
npm start
```

Browser will open at http://localhost:3000

## Step 5: Test the Application

### 5.1 Sign Up
1. Click "Create Account"
2. Enter email, name, and password
3. Check your email for verification code
4. Enter the code

### 5.2 Sign In
1. Enter your email and password
2. You'll see the products page

### 5.3 Complete Order Flow
1. Browse products
2. Add items to cart
3. Go to Cart page
4. Click "Place Order"
5. Check Orders page

🎉 **Everything works with real AWS Cognito authentication!**

## What's Running

- **Frontend**: http://localhost:3000 (React app)
- **API Gateway**: http://localhost:8080 (Nginx)
- **Backend Services**: Ports 8001-8004
- **PostgreSQL**: Port 5432
- **LocalStack**: Port 4566 (DynamoDB, SNS, SQS, SES)

## Troubleshooting

### "Auth UserPool not configured"
- Make sure you updated `aws-config.js` with your real credentials
- Restart the React app

### "USER_SRP_AUTH is not enabled"
- Go to Cognito → App client → Edit
- Enable ALLOW_USER_SRP_AUTH
- Save changes

### Services not starting
```bash
cd local-deployment
docker-compose down
docker-compose up --build
```

### Port conflicts
- Make sure ports 3000, 8080, 8001-8004, 5432, 4566 are free
- Stop any conflicting services

## Cost

- **Cognito**: Free tier (50,000 MAUs/month)
- **Local testing**: $0 (everything runs locally)
- **Your usage**: ~1-5 test users = **$0.00**

## Next Steps

Once local testing works:
1. Follow AWS deployment guides (coming next)
2. Deploy to real AWS infrastructure
3. Learn Terraform for automation (optional)

## Need Help?

Check the documentation:
- `docs/architecture.md` - System architecture
- `docs/local-setup.md` - Detailed local setup
- `docs/COGNITO_SETUP_GUIDE.md` - Cognito details
- `TESTING_GUIDE.md` - Testing instructions

## What You're Learning

✅ Microservices architecture
✅ AWS Cognito authentication
✅ React + FastAPI integration
✅ DynamoDB and PostgreSQL
✅ Event-driven architecture (SNS/SQS)
✅ Docker and containerization
✅ API Gateway patterns
✅ Real-world AWS development

Happy learning! 🚀
