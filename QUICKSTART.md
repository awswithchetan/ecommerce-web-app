# eCommerce AWS Tutorial - Quick Start Guide

## Prerequisites

- AWS Account (free tier)
- EC2 instance or local Linux/Mac machine

## Step 1: Install Prerequisites

### On EC2 (Amazon Linux 2023/AL2):

```bash
# Install git first
sudo yum install git -y

# Clone the repository
git clone https://github.com/awswithchetan/ecommerce-web-app.git
cd ecommerce-web-app

# Run installation script
chmod +x install-prerequisites.sh
./install-prerequisites.sh

# Log out and back in for Docker group changes
exit
# SSH back into your instance
```

### On Local Machine:
Ensure you have Docker, Docker Compose, and Node.js 20+ installed.

```bash
git clone https://github.com/awswithchetan/ecommerce-web-app.git
cd ecommerce-web-app
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

Choose your deployment environment:

---

### Option A: Local Development (Recommended for First-Time Setup)

#### 4A.1 Start Backend Services

```bash
cd local-deployment
docker compose up --build
```

Wait for all services to start (~2 minutes).

#### 4A.2 Create and Configure .env File

```bash
cd ../frontend/react-app

# Create .env file
cat > .env << 'EOF'
REACT_APP_API_URL=http://localhost:8080/api
EOF
```

#### 4A.3 Start Frontend

```bash
npm install
npm start
```

Browser will automatically open at http://localhost:3000

✅ **You're ready to test!** Skip to Step 5.

---

### Option B: EC2 Deployment

#### 4B.1 Configure EC2 Security Group

In AWS Console → EC2 → Security Groups → Your instance's security group:

Add these **Inbound Rules**:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | Your IP | SSH access |
| Custom TCP | TCP | 3000 | 0.0.0.0/0 | Frontend |
| Custom TCP | TCP | 8080 | 0.0.0.0/0 | API Gateway |

#### 4B.2 Get EC2 Public IP

```bash
# On EC2 instance, run:
curl http://checkip.amazonaws.com
```

Or find it in AWS Console → EC2 → Instances → Your instance → Public IPv4 address

#### 4B.3 Start Backend Services

```bash
cd local-deployment
docker compose up --build -d
```

#### 4B.4 Create and Configure .env File

```bash
cd ../frontend/react-app

# Replace <EC2-PUBLIC-IP> with your actual IP
cat > .env << 'EOF'
REACT_APP_API_URL=http://<EC2-PUBLIC-IP>:8080/api
EOF

# Edit the file to add your actual IP
nano .env
```

#### 4B.5 Start Frontend

```bash
npm install
HOST=0.0.0.0 npm start
```

**Note:** `HOST=0.0.0.0` makes the app accessible from outside the EC2 instance.

#### 4B.6 Access the Application

Open your browser and go to:
```
http://<EC2-PUBLIC-IP>:3000
```

✅ **You're ready to test!**

---

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
