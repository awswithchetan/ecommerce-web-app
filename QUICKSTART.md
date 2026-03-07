# eCommerce AWS Tutorial - Quick Start Guide

## Choose Your Deployment Option

This guide provides two deployment paths:

- **[Option 1: Local Development](#option-1-local-development)** - Run everything on your local machine (Recommended for learning)
- **[Option 2: EC2 Deployment](#option-2-ec2-deployment)** - Deploy on AWS EC2 instance (For testing in cloud)

---

# Option 1: Local Development

## Step 1: Install Prerequisites

Ensure you have installed:
- Docker and Docker Compose
- Node.js 20+
- Git

### Installation Commands (Linux/Mac):

```bash
# Check if already installed
docker --version
node --version
git --version
```

If not installed, follow the official installation guides for your OS.

## Step 2: Clone the Repository

```bash
git clone https://github.com/awswithchetan/ecommerce-web-app.git
cd ecommerce-web-app
```

## Step 3: Create AWS Cognito User Pool

### 3.1 Go to AWS Console
1. Log into AWS Console: https://console.aws.amazon.com
2. **Select Region**: ap-south-1 (Mumbai) - top right corner
3. Search for "Cognito" and click on it
4. Click **"Create user pool"**

### 3.2 Configure User Pool

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

### 3.3 Get Your Credentials

After creation:
1. Copy **User Pool ID** (looks like: `ap-south-1_xxxxxxxxx`)
2. Go to "App integration" tab
3. Click on your app client
4. Copy **Client ID** (long string)

## Step 4: Configure AWS Credentials

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

## Step 5: Start Backend Services

```bash
cd local-deployment
docker compose up --build
```

Wait for all services to start (~2 minutes). You should see:
- ✅ LocalStack running
- ✅ PostgreSQL running
- ✅ All 5 microservices running
- ✅ Nginx running

## Step 6: Start Frontend

Open a new terminal:

```bash
cd frontend/react-app
npm install
npm start
```

Browser will automatically open at http://localhost:3000

## Step 7: Test the Application

### 7.1 Sign Up
1. Click "Create Account"
2. Enter email, name, and password
3. Check your email for verification code
4. Enter the code

### 7.2 Sign In
1. Enter your email and password
2. You'll see the products page

### 7.3 Complete Order Flow
1. Browse products
2. Add items to cart
3. Go to Cart page
4. Click "Place Order"
5. Check Orders page

🎉 **Everything works with real AWS Cognito authentication!**

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
docker compose down
docker compose up --build
```

### Port conflicts
- Make sure ports 3000, 8080, 8001-8004, 5432, 4566 are free
- Stop any conflicting services

---

# Option 2: EC2 Deployment

## Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → Launch Instance
2. Choose **Amazon Linux 2023** AMI
3. Instance type: **t2.medium** or larger (t2.micro may be slow)
4. Create or select a key pair for SSH access
5. Launch instance

## Step 2: Configure Security Group

In AWS Console → EC2 → Security Groups → Your instance's security group:

Add these **Inbound Rules**:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | Your IP | SSH access |
| Custom TCP | TCP | 3000 | 0.0.0.0/0 | Frontend |
| Custom TCP | TCP | 8080 | 0.0.0.0/0 | API Gateway |

## Step 3: Connect to EC2 and Install Prerequisites

```bash
# SSH into your instance
ssh -i your-key.pem ec2-user@<EC2-PUBLIC-IP>

# Install git
sudo yum install git -y

# Clone the repository
git clone https://github.com/awswithchetan/ecommerce-web-app.git
cd ecommerce-web-app

# Run installation script
chmod +x install-prerequisites.sh
./install-prerequisites.sh

# Log out and back in for Docker group changes
exit
```

SSH back into your instance:
```bash
ssh -i your-key.pem ec2-user@<EC2-PUBLIC-IP>
cd ecommerce-web-app
```

## Step 4: Get EC2 Public IP

```bash
curl http://checkip.amazonaws.com
```

Save this IP - you'll need it for configuration.

## Step 5: Create AWS Cognito User Pool

### 5.1 Go to AWS Console
1. Log into AWS Console: https://console.aws.amazon.com
2. **Select Region**: ap-south-1 (Mumbai) - top right corner
3. Search for "Cognito" and click on it
4. Click **"Create user pool"**

### 5.2 Configure User Pool

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
- Callback URL: `http://<EC2-PUBLIC-IP>:3000` ⚠️ **Use your actual EC2 IP**
- Authentication flows: 
  - ☑ ALLOW_USER_SRP_AUTH
  - ☑ ALLOW_REFRESH_TOKEN_AUTH
- Click Next

**Step 6 - Review and create:**
- Click **Create user pool**

**Note:** Cognito requires HTTPS for non-localhost URLs. For testing, you can:
- Use SSH tunnel: `ssh -L 3000:localhost:3000 -L 8080:localhost:8080 ec2-user@<EC2-IP>` and keep callback as `http://localhost:3000`
- Or set up HTTPS (advanced, not covered in quick start)

### 5.3 Get Your Credentials

After creation:
1. Copy **User Pool ID** (looks like: `ap-south-1_xxxxxxxxx`)
2. Go to "App integration" tab
3. Click on your app client
4. Copy **Client ID** (long string)

## Step 6: Configure the Application

### 6.1 Update AWS Credentials

Edit: `frontend/react-app/src/aws-config.js`

```bash
nano frontend/react-app/src/aws-config.js
```

Replace the placeholder values with your Cognito credentials.

### 6.2 Update API URL

Edit: `frontend/react-app/.env`

```bash
nano frontend/react-app/.env
```

Change to:
```
REACT_APP_API_URL=http://<EC2-PUBLIC-IP>:8080/api
```

Replace `<EC2-PUBLIC-IP>` with your actual IP.

## Step 7: Start Backend Services

```bash
cd local-deployment
docker compose up --build -d
```

The `-d` flag runs containers in the background.

## Step 8: Start Frontend

```bash
cd ../frontend/react-app
npm install
HOST=0.0.0.0 npm start
```

**Note:** `HOST=0.0.0.0` makes the app accessible from outside the EC2 instance.

## Step 9: Access the Application

Open your browser and go to:
```
http://<EC2-PUBLIC-IP>:3000
```

## Step 10: Test the Application

### 10.1 Sign Up
1. Click "Create Account"
2. Enter email, name, and password
3. Check your email for verification code
4. Enter the code

### 10.2 Sign In
1. Enter your email and password
2. You'll see the products page

### 10.3 Complete Order Flow
1. Browse products
2. Add items to cart
3. Go to Cart page
4. Click "Place Order"
5. Check Orders page

🎉 **Your app is running on EC2!**

## Troubleshooting

### Cannot connect to frontend
- Check security group has port 3000 open
- Verify npm is running with `HOST=0.0.0.0`
- Check EC2 public IP hasn't changed (happens on stop/start)

### Cognito HTTPS error
- Use SSH tunnel method (see Step 5.2 note)
- Or keep callback as localhost and access via tunnel

### Services not starting
```bash
cd local-deployment
docker compose down
docker compose up --build -d
```

### Check logs
```bash
docker compose logs -f
```

---

## What's Running

- **Frontend**: Port 3000 (React app)
- **API Gateway**: Port 8080 (Nginx)
- **Backend Services**: Ports 8001-8004
- **PostgreSQL**: Port 5432
- **LocalStack**: Port 4566 (DynamoDB, SNS, SQS, SES)
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

## What's Running

- **Frontend**: Port 3000 (React app)
- **API Gateway**: Port 8080 (Nginx)
- **Backend Services**: Ports 8001-8004
- **PostgreSQL**: Port 5432
- **LocalStack**: Port 4566 (DynamoDB, SNS, SQS, SES)

## Cost Estimates

### Local Development
- **Cost**: $0 (everything runs locally)
- **Cognito**: Free tier (50,000 MAUs/month)

### EC2 Deployment
- **EC2 t2.medium**: ~$0.05/hour (~$1.20/day)
- **Cognito**: Free tier
- **Data transfer**: Minimal for testing
- **Total for 4-hour session**: ~$0.20

## Next Steps

Once testing works:
1. Follow AWS deployment guides for production setup
2. Deploy to real AWS infrastructure (ECS, RDS, etc.)
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
