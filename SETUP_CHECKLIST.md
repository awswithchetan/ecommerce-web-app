# Student Setup Checklist

Use this checklist to ensure you've completed all setup steps correctly.

## ☐ Prerequisites

- [ ] Docker installed and running
- [ ] Docker Compose installed (or Docker with compose plugin)
- [ ] Node.js 18+ installed
- [ ] AWS Account created (free tier)
- [ ] Git installed

## ☐ AWS Cognito Setup

- [ ] Logged into AWS Console
- [ ] Selected ap-south-1 (Mumbai) region
- [ ] Created Cognito User Pool named `ecommerce-user-pool`
- [ ] Selected "Email" as sign-in option
- [ ] Enabled self-service sign-up
- [ ] Created app client as "Single-page application"
- [ ] Enabled ALLOW_USER_SRP_AUTH flow
- [ ] Copied User Pool ID (format: ap-south-1_xxxxxxxxx)
- [ ] Copied Client ID (long alphanumeric string)

## ☐ Application Configuration

- [ ] Cloned the repository
- [ ] Opened `frontend/react-app/src/aws-config.js`
- [ ] Replaced `YOUR_USER_POOL_ID_HERE` with actual User Pool ID
- [ ] Replaced `YOUR_CLIENT_ID_HERE` with actual Client ID
- [ ] Saved the file

## ☐ Backend Setup

- [ ] Opened terminal in `local-deployment` directory
- [ ] Ran `docker-compose up --build`
- [ ] Waited for all services to start
- [ ] Verified LocalStack is running (healthy status)
- [ ] Verified PostgreSQL is running (healthy status)
- [ ] Verified all 5 services are running (product, cart, user, order, notification)
- [ ] Verified Nginx is running

## ☐ Frontend Setup

- [ ] Opened new terminal in `frontend/react-app` directory
- [ ] Ran `npm install`
- [ ] Waited for dependencies to install
- [ ] Ran `npm start`
- [ ] Browser opened to http://localhost:3000
- [ ] Saw Cognito login/signup screen

## ☐ Testing Authentication

- [ ] Clicked "Create Account"
- [ ] Entered email, name, and password
- [ ] Received verification code email
- [ ] Entered verification code
- [ ] Successfully logged in
- [ ] Saw products page with 3 products
- [ ] Saw my email/name in navbar
- [ ] Saw "Sign Out" button

## ☐ Testing Application Flow

- [ ] Clicked "Add to Cart" on a product
- [ ] Saw success message
- [ ] Clicked "Cart" in navigation
- [ ] Saw item in cart
- [ ] Clicked "Place Order"
- [ ] Saw order success message
- [ ] Cart was cleared
- [ ] Clicked "Orders" in navigation
- [ ] Saw my order with details

## ☐ Testing Sign Out/In

- [ ] Clicked "Sign Out"
- [ ] Returned to login screen
- [ ] Signed in again with same credentials
- [ ] Saw my previous orders still there

## ✅ Success!

If all items are checked, you have successfully:
- ✅ Set up AWS Cognito authentication
- ✅ Configured the application
- ✅ Started all backend services
- ✅ Started the frontend
- ✅ Tested complete user flow
- ✅ Verified data persistence

## 🎉 What's Next?

You're ready to:
1. Explore the codebase
2. Understand the architecture
3. Prepare for AWS deployment
4. Learn about each AWS service used

## ❌ Troubleshooting

If any step failed, check:
- [ ] `QUICKSTART.md` for detailed instructions
- [ ] `TESTING_GUIDE.md` for troubleshooting tips
- [ ] Docker logs: `docker-compose logs <service-name>`
- [ ] Browser console for frontend errors
- [ ] AWS Cognito configuration is correct

## 📊 What You've Learned

By completing this setup, you've worked with:
- ✅ AWS Cognito (Authentication)
- ✅ Docker & Docker Compose (Containerization)
- ✅ React (Frontend)
- ✅ FastAPI (Backend)
- ✅ PostgreSQL (Relational Database)
- ✅ DynamoDB (NoSQL Database)
- ✅ LocalStack (AWS Emulation)
- ✅ Microservices Architecture
- ✅ Event-Driven Systems (SNS/SQS)

Great job! 🚀
