# Module 3: Authentication with Cognito

## Overview
Set up AWS Cognito User Pool for user authentication and authorization.

## Architecture
```
Cognito User Pool
├── User Pool: ecommerce-users
├── App Client: ecommerce-web-client
├── Domain: ecommerce-<random>.auth.ap-south-1.amazoncognito.com
└── Hosted UI (optional)
```

## Resources to Create

### 1. Cognito User Pool
- Name: ecommerce-users
- Sign-in options: Email
- Password policy: Default
- MFA: Optional (off for dev)
- Email provider: Cognito (for dev)

### 2. App Client
- Name: ecommerce-web-client
- Client type: Public client
- Authentication flows: ALLOW_USER_PASSWORD_AUTH, ALLOW_REFRESH_TOKEN_AUTH
- OAuth 2.0 flows: Authorization code grant
- Callback URLs: http://localhost:3000 (for local dev)
- Sign out URLs: http://localhost:3000

### 3. Hosted UI Domain (Optional)
- Domain prefix: ecommerce-<your-unique-id>

## Console Steps

### Step 1: Create User Pool

1. Go to Cognito Console → User Pools
2. Click "Create user pool"

**Configure sign-in experience:**
3. Cognito user pool sign-in options:
   - Select: Email
4. User name requirements: Keep defaults
5. Click "Next"

**Configure security requirements:**
6. Password policy:
   - Mode: Cognito defaults
   - MFA: No MFA (for dev)
7. User account recovery:
   - Enable self-service account recovery: Yes
   - Delivery method: Email only
8. Click "Next"

**Configure sign-up experience:**
9. Self-service sign-up: Enable
10. Attribute verification:
    - Allow Cognito to automatically send messages: Yes
    - Attributes to verify: Email
11. Required attributes:
    - email (already selected)
    - name (add this)
12. Click "Next"

**Configure message delivery:**
13. Email provider: Send email with Cognito (for dev)
14. FROM email address: no-reply@verificationemail.com (default)
15. Click "Next"

**Integrate your app:**
16. User pool name: `ecommerce-users`
17. Hosted authentication pages: Use Cognito Hosted UI (optional)
18. Domain type: Use a Cognito domain
19. Cognito domain: `ecommerce-<random-number>` (must be unique)
20. Initial app client:
    - App type: Public client
    - App client name: `ecommerce-web-client`
    - Client secret: Don't generate a client secret
21. Advanced app client settings:
    - Authentication flows:
      - ✅ ALLOW_USER_PASSWORD_AUTH
      - ✅ ALLOW_REFRESH_TOKEN_AUTH
      - ✅ ALLOW_USER_SRP_AUTH
22. Click "Next"

**Review and create:**
23. Review all settings
24. Click "Create user pool"

### Step 2: Configure App Client (if needed)

1. Go to your user pool → App integration tab
2. Click on your app client
3. Edit Hosted UI settings:
   - Allowed callback URLs: `http://localhost:3000`
   - Allowed sign-out URLs: `http://localhost:3000`
   - OAuth 2.0 grant types:
     - ✅ Authorization code grant
     - ✅ Implicit grant
   - OpenID Connect scopes:
     - ✅ OpenID
     - ✅ Email
     - ✅ Profile
4. Save changes

### Step 3: Note Important Values

From the User Pool page, note down:
- User Pool ID (e.g., `ap-south-1_xxxxxxxxx`)
- User Pool ARN
- App Client ID (from App integration tab)
- Cognito Domain (from App integration → Domain)

## CLI Commands

### Create User Pool
```bash
USER_POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name ecommerce-users \
  --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=false}" \
  --auto-verified-attributes email \
  --username-attributes email \
  --schema Name=email,Required=true,Mutable=true Name=name,Required=true,Mutable=true \
  --account-recovery-setting "RecoveryMechanisms=[{Priority=1,Name=verified_email}]" \
  --email-configuration EmailSendingAccount=COGNITO_DEFAULT \
  --region ap-south-1 \
  --query 'UserPool.Id' \
  --output text)

echo "User Pool ID: $USER_POOL_ID"
echo "USER_POOL_ID=$USER_POOL_ID" >> deployment/vpc-resources.txt
```

### Create App Client
```bash
APP_CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-name ecommerce-web-client \
  --no-generate-secret \
  --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH ALLOW_USER_SRP_AUTH \
  --supported-identity-providers COGNITO \
  --callback-urls "http://localhost:3000" \
  --logout-urls "http://localhost:3000" \
  --allowed-o-auth-flows authorization_code implicit \
  --allowed-o-auth-scopes openid email profile \
  --allowed-o-auth-flows-user-pool-client \
  --region ap-south-1 \
  --query 'UserPoolClient.ClientId' \
  --output text)

echo "App Client ID: $APP_CLIENT_ID"
echo "APP_CLIENT_ID=$APP_CLIENT_ID" >> deployment/vpc-resources.txt
```

### Create Cognito Domain
```bash
DOMAIN_PREFIX="ecommerce-$RANDOM"

aws cognito-idp create-user-pool-domain \
  --domain $DOMAIN_PREFIX \
  --user-pool-id $USER_POOL_ID \
  --region ap-south-1

echo "Cognito Domain: https://$DOMAIN_PREFIX.auth.ap-south-1.amazoncognito.com"
echo "COGNITO_DOMAIN=$DOMAIN_PREFIX" >> deployment/vpc-resources.txt
```

### Get User Pool Details
```bash
aws cognito-idp describe-user-pool \
  --user-pool-id $USER_POOL_ID \
  --region ap-south-1 \
  --query 'UserPool.[Id,Name,Arn]' \
  --output table
```

## Update Frontend Configuration

Update `frontend/react-app/src/aws-config.js`:

```javascript
const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: 'ap-south-1_xxxxxxxxx',  // Your User Pool ID
      userPoolClientId: 'xxxxxxxxxxxxxxxxxxxxxxxxxx',  // Your App Client ID
      loginWith: {
        oauth: {
          domain: 'ecommerce-xxxxx.auth.ap-south-1.amazoncognito.com',
          scopes: ['openid', 'email', 'profile'],
          redirectSignIn: ['http://localhost:3000'],
          redirectSignOut: ['http://localhost:3000'],
          responseType: 'code'
        }
      }
    }
  }
};

export default awsConfig;
```

## Testing Authentication

### Test User Creation (Console)
1. Go to Cognito → User pools → ecommerce-users
2. Users tab → Create user
3. Email: test@example.com
4. Temporary password: TempPass123!
5. Create user

### Test User Creation (CLI)
```bash
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username test@example.com \
  --user-attributes Name=email,Value=test@example.com Name=name,Value="Test User" \
  --temporary-password "TempPass123!" \
  --message-action SUPPRESS \
  --region ap-south-1
```

### Test Authentication Flow
```bash
# Initiate auth
aws cognito-idp admin-initiate-auth \
  --user-pool-id $USER_POOL_ID \
  --client-id $APP_CLIENT_ID \
  --auth-flow ADMIN_USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=test@example.com,PASSWORD=TempPass123! \
  --region ap-south-1
```

## Hosted UI URL
```
https://<domain-prefix>.auth.ap-south-1.amazoncognito.com/login?client_id=<app-client-id>&response_type=code&redirect_uri=http://localhost:3000
```

## Verification

### List Users
```bash
aws cognito-idp list-users \
  --user-pool-id $USER_POOL_ID \
  --region ap-south-1
```

### Get User Pool Info
```bash
aws cognito-idp describe-user-pool \
  --user-pool-id $USER_POOL_ID \
  --region ap-south-1
```

## Cost Considerations
- First 50,000 MAUs (Monthly Active Users): Free
- Beyond that: $0.0055 per MAU
- For dev/testing: Essentially free

## Cleanup Commands
```bash
# Delete user pool domain
aws cognito-idp delete-user-pool-domain \
  --domain $COGNITO_DOMAIN \
  --user-pool-id $USER_POOL_ID \
  --region ap-south-1

# Delete user pool (this also deletes app clients)
aws cognito-idp delete-user-pool \
  --user-pool-id $USER_POOL_ID \
  --region ap-south-1
```

## Next Steps
After completing this module:
- ✅ Cognito User Pool configured
- ✅ App client created
- ✅ Frontend can authenticate users
- Ready for Module 4: Container Deployment (ECS)
