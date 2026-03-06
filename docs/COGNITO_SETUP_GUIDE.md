# Adding AWS Cognito Authentication - Step by Step Guide

## Part 1: Create Cognito User Pool (AWS Console)

### Step 1: Go to AWS Cognito

1. Log into AWS Console: https://console.aws.amazon.com
2. Search for "Cognito" in the search bar
3. Click on "Amazon Cognito"
4. Click **"Create user pool"**

### Step 2: Configure Sign-in Experience

**Authentication providers:**
- Select: ☑ **Email**
- Click **Next**

### Step 3: Configure Security Requirements

**Password policy:**
- Select: **Cognito defaults** (or customize if you want)

**Multi-factor authentication:**
- Select: **No MFA** (for simplicity in tutorial)

**User account recovery:**
- Select: ☑ **Email only**

Click **Next**

### Step 4: Configure Sign-up Experience

**Self-service sign-up:**
- Enable: ☑ **Allow users to sign themselves up**

**Attribute verification:**
- Select: ☑ **Send email message, verify email address**

**Required attributes:**
- Select: ☑ **name** (optional, but recommended)
- Select: ☑ **email** (should be auto-selected)

Click **Next**

### Step 5: Configure Message Delivery

**Email provider:**
- Select: ◉ **Send email with Amazon SES - Recommended**
- OR: ◉ **Send email with Cognito** (easier for testing, has limits)

**SES Region:** (if using SES)
- Select: **ap-south-1** (Asia Pacific Mumbai)

**FROM email address:**
- Use default or enter your verified email

Click **Next**

### Step 6: Integrate Your App

**User pool name:**
- Enter: `ecommerce-user-pool`

**Hosted authentication pages:**
- Select: ☐ **Don't use Cognito Hosted UI** (we'll use custom UI)

**Initial app client:**
- App client name: `ecommerce-web-client`
- Client secret: ◉ **Don't generate a client secret** (for public web apps)

**Advanced app client settings:**
- Authentication flows: ☑ **ALLOW_USER_PASSWORD_AUTH**
- Authentication flows: ☑ **ALLOW_REFRESH_TOKEN_AUTH**

Click **Next**

### Step 7: Review and Create

- Review all settings
- Click **Create user pool**

### Step 8: Get Your Configuration Details

After creation, you'll see your User Pool. **Copy these values:**

1. **User Pool ID**: 
   - Found at the top (looks like: `ap-south-1_xxxxxxxxx`)
   - Copy this value

2. **App Client ID**:
   - Click on "App integration" tab
   - Scroll down to "App clients and analytics"
   - Click on your app client name
   - Copy the **Client ID** (looks like: `1a2b3c4d5e6f7g8h9i0j1k2l3m`)

---

## Part 2: Configure Frontend with Cognito

### Step 1: Install AWS Amplify

Open terminal in your project:

```bash
cd /home/chetan/ecommerce-aws-tutorial/frontend/react-app
npm install aws-amplify @aws-amplify/ui-react
```

### Step 2: Create Cognito Configuration File

Create file: `src/aws-config.js`

```javascript
const awsConfig = {
  Auth: {
    region: 'ap-south-1',  // Mumbai region
    userPoolId: 'ap-south-1_XXXXXXXXX',  // YOUR USER POOL ID HERE
    userPoolWebClientId: 'XXXXXXXXXXXXXXXXXXXXXXXXXX',  // YOUR APP CLIENT ID HERE
  }
};

export default awsConfig;
```

**Replace:**
- `ap-south-1_XXXXXXXXX` with your User Pool ID
- `XXXXXXXXXXXXXXXXXXXXXXXXXX` with your App Client ID

### Step 3: Tell Me When You're Done

Once you've:
1. ✅ Created the Cognito User Pool
2. ✅ Copied the User Pool ID and App Client ID
3. ✅ Installed AWS Amplify
4. ✅ Created the aws-config.js file with your IDs

**Let me know**, and I'll:
- Create the Login/Signup pages
- Update the API integration
- Add authentication to all protected routes
- Test the complete flow

---

## What You'll Get

After integration:
- ✅ Real login/signup pages
- ✅ Email verification
- ✅ Password reset
- ✅ JWT tokens
- ✅ Protected routes
- ✅ User-specific cart and orders
- ✅ Logout functionality

---

## Estimated Time

- Creating Cognito User Pool: **5 minutes**
- Installing dependencies: **2 minutes**
- Creating config file: **1 minute**

**Total: ~8 minutes**

---

## Cost

- **Free Tier**: 50,000 Monthly Active Users
- **Your testing**: ~1-5 users
- **Cost**: $0.00

---

## Need Help?

If you get stuck at any step, let me know which step and I'll provide more detailed guidance!

## Ready?

Start with **Part 1, Step 1** and work through the AWS Console steps. Let me know when you have your User Pool ID and App Client ID!
