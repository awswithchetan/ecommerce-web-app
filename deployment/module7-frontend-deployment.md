# Module 7: Frontend Deployment (S3 + CloudFront)

## Overview
Deploy the React frontend as a static website using S3 and CloudFront for global content delivery.

## Architecture
```
User → CloudFront (CDN) → S3 Bucket (Static Website)
                ↓
        API Gateway (Backend APIs)
```

## Why S3 + CloudFront?
- S3: Cost-effective static website hosting
- CloudFront: Global CDN for fast content delivery
- HTTPS: Free SSL certificate with CloudFront
- Caching: Reduced load on origin, faster response
- Security: Origin Access Identity (OAI) to restrict S3 access

## Resources to Create

### 1. S3 Bucket
- Name: ecommerce-frontend-<unique-id>
- Purpose: Store React build files
- Public access: Blocked (CloudFront will access via OAI)

### 2. CloudFront Distribution
- Origin: S3 bucket
- Default root object: index.html
- Error pages: Redirect to index.html (for React Router)
- SSL: CloudFront default certificate

### 3. Origin Access Identity (OAI)
- Allows CloudFront to access private S3 bucket

## Console Steps

### Step 1: Build React Application

1. Update frontend configuration with production values:

**Update `frontend/react-app/.env.production`:**
```
REACT_APP_API_URL=https://<api-id>.execute-api.ap-south-1.amazonaws.com
```

**Update `frontend/react-app/src/aws-config.js`:**
```javascript
const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: 'ap-south-1_xxxxxxxxx',
      userPoolClientId: 'xxxxxxxxxxxxxxxxxxxxxxxxxx',
      loginWith: {
        oauth: {
          domain: 'ecommerce-xxxxx.auth.ap-south-1.amazoncognito.com',
          scopes: ['openid', 'email', 'profile'],
          redirectSignIn: ['https://<cloudfront-domain>'],  // Update after CloudFront creation
          redirectSignOut: ['https://<cloudfront-domain>'],
          responseType: 'code'
        }
      }
    }
  }
};
```

2. Build the application:
```bash
cd frontend/react-app
npm run build
```

This creates a `build/` directory with optimized production files.

### Step 2: Create S3 Bucket

1. Go to S3 Console → Create bucket
2. Bucket name: `ecommerce-frontend-<random-number>` (must be globally unique)
3. Region: ap-south-1
4. Block all public access: ✅ Enable (CloudFront will access it)
5. Bucket versioning: Disable (optional: enable for rollback capability)
6. Encryption: Enable (SSE-S3)
7. Create bucket

### Step 3: Upload Build Files to S3

1. Open your bucket
2. Click "Upload"
3. Add files: Select all files from `frontend/react-app/build/` directory
4. Upload

**Or use CLI:**
```bash
aws s3 sync frontend/react-app/build/ s3://ecommerce-frontend-<id>/ --region ap-south-1
```

### Step 4: Create CloudFront Origin Access Identity

1. Go to CloudFront Console → Origin access → Origin access identities
2. Create origin access identity
3. Name: `ecommerce-s3-oai`
4. Comment: "OAI for ecommerce frontend"
5. Create

### Step 5: Update S3 Bucket Policy

1. Go to S3 bucket → Permissions → Bucket policy
2. Add policy to allow CloudFront OAI:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity <OAI-ID>"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::ecommerce-frontend-<id>/*"
    }
  ]
}
```

### Step 6: Create CloudFront Distribution

1. CloudFront Console → Create distribution
2. Origin settings:
   - Origin domain: Select your S3 bucket
   - Origin path: Leave empty
   - Name: Auto-filled
   - Origin access: Origin access control settings (recommended)
     - Or use Legacy: Origin access identity → Select your OAI
   - Enable Origin Shield: No
3. Default cache behavior:
   - Viewer protocol policy: Redirect HTTP to HTTPS
   - Allowed HTTP methods: GET, HEAD, OPTIONS
   - Cache policy: CachingOptimized
   - Origin request policy: None
4. Settings:
   - Price class: Use all edge locations (or select based on your audience)
   - Alternate domain name (CNAME): Leave empty (or add custom domain)
   - SSL certificate: Default CloudFront certificate
   - Default root object: `index.html`
5. Create distribution (takes 10-15 minutes to deploy)

### Step 7: Configure Error Pages (for React Router)

1. Go to your distribution → Error pages tab
2. Create custom error response:
   - HTTP error code: 403
   - Customize error response: Yes
   - Response page path: `/index.html`
   - HTTP response code: 200
3. Create another:
   - HTTP error code: 404
   - Customize error response: Yes
   - Response page path: `/index.html`
   - HTTP response code: 200

This ensures React Router handles all routes.

### Step 8: Update Cognito Callback URLs

1. Go to Cognito Console → User pools → ecommerce-users
2. App integration → App client
3. Edit Hosted UI settings:
   - Add callback URL: `https://<cloudfront-domain>`
   - Add sign-out URL: `https://<cloudfront-domain>`
4. Save changes

### Step 9: Test the Application

1. Get CloudFront domain: `https://d1234567890abc.cloudfront.net`
2. Open in browser
3. Test:
   - Browse products
   - Sign up / Sign in
   - Add to cart
   - Place order
   - Check email for confirmation

## CLI Commands

### Build React App
```bash
cd frontend/react-app

# Update .env.production with API Gateway URL
cat > .env.production <<EOF
REACT_APP_API_URL=$API_ENDPOINT
EOF

# Build
npm run build
cd ../..
```

### Create S3 Bucket
```bash
BUCKET_NAME="ecommerce-frontend-$RANDOM"

aws s3 mb s3://$BUCKET_NAME --region ap-south-1

# Block public access
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true \
  --region ap-south-1

echo "BUCKET_NAME=$BUCKET_NAME" >> deployment/vpc-resources.txt
```

### Upload Build Files
```bash
aws s3 sync frontend/react-app/build/ s3://$BUCKET_NAME/ \
  --region ap-south-1 \
  --delete
```

### Create CloudFront OAI
```bash
OAI_ID=$(aws cloudfront create-cloud-front-origin-access-identity \
  --cloud-front-origin-access-identity-config \
    CallerReference=$(date +%s),Comment="OAI for ecommerce frontend" \
  --query 'CloudFrontOriginAccessIdentity.Id' \
  --output text)

echo "OAI_ID=$OAI_ID" >> deployment/vpc-resources.txt
```

### Update S3 Bucket Policy
```bash
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity $OAI_ID"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket $BUCKET_NAME \
  --policy file:///tmp/bucket-policy.json \
  --region ap-south-1
```

### Create CloudFront Distribution
```bash
cat > /tmp/cf-config.json <<EOF
{
  "CallerReference": "$(date +%s)",
  "Comment": "Ecommerce Frontend Distribution",
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-$BUCKET_NAME",
        "DomainName": "$BUCKET_NAME.s3.ap-south-1.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": "origin-access-identity/cloudfront/$OAI_ID"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-$BUCKET_NAME",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 3,
      "Items": ["GET", "HEAD", "OPTIONS"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "Compress": true,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {"Forward": "none"}
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000,
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    }
  },
  "CustomErrorResponses": {
    "Quantity": 2,
    "Items": [
      {
        "ErrorCode": 403,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 300
      },
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 300
      }
    ]
  },
  "Enabled": true
}
EOF

CF_DISTRIBUTION_ID=$(aws cloudfront create-distribution \
  --distribution-config file:///tmp/cf-config.json \
  --query 'Distribution.Id' \
  --output text)

CF_DOMAIN=$(aws cloudfront get-distribution \
  --id $CF_DISTRIBUTION_ID \
  --query 'Distribution.DomainName' \
  --output text)

echo "CF_DISTRIBUTION_ID=$CF_DISTRIBUTION_ID" >> deployment/vpc-resources.txt
echo "CF_DOMAIN=$CF_DOMAIN" >> deployment/vpc-resources.txt
echo "CloudFront Domain: https://$CF_DOMAIN"
```

### Wait for Distribution to Deploy
```bash
echo "Waiting for CloudFront distribution to deploy (this takes 10-15 minutes)..."
aws cloudfront wait distribution-deployed \
  --id $CF_DISTRIBUTION_ID

echo "Distribution deployed!"
```

### Update Cognito Callback URLs
```bash
# Get current app client config
aws cognito-idp describe-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-id $APP_CLIENT_ID \
  --region ap-south-1

# Update with CloudFront domain
aws cognito-idp update-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-id $APP_CLIENT_ID \
  --callback-urls "http://localhost:3000" "https://$CF_DOMAIN" \
  --logout-urls "http://localhost:3000" "https://$CF_DOMAIN" \
  --region ap-south-1
```

## Updating the Frontend

When you make changes to the React app:

```bash
# 1. Build
cd frontend/react-app
npm run build

# 2. Upload to S3
aws s3 sync build/ s3://$BUCKET_NAME/ --delete --region ap-south-1

# 3. Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id $CF_DISTRIBUTION_ID \
  --paths "/*"
```

## Verification

### Check S3 Files
```bash
aws s3 ls s3://$BUCKET_NAME/ --recursive --region ap-south-1
```

### Check CloudFront Status
```bash
aws cloudfront get-distribution \
  --id $CF_DISTRIBUTION_ID \
  --query 'Distribution.[Id,Status,DomainName]' \
  --output table
```

### Test Website
```bash
curl -I https://$CF_DOMAIN
```

## Performance Optimization

### Enable Compression
CloudFront automatically compresses files (already configured above).

### Set Cache Headers in S3
```bash
# Set cache headers for static assets
aws s3 cp s3://$BUCKET_NAME/static/ s3://$BUCKET_NAME/static/ \
  --recursive \
  --metadata-directive REPLACE \
  --cache-control "public, max-age=31536000, immutable" \
  --region ap-south-1

# Set cache headers for index.html (no cache)
aws s3 cp s3://$BUCKET_NAME/index.html s3://$BUCKET_NAME/index.html \
  --metadata-directive REPLACE \
  --cache-control "no-cache, no-store, must-revalidate" \
  --region ap-south-1
```

## Monitoring

### CloudFront Metrics
- Requests
- Bytes downloaded
- Error rate (4xx, 5xx)
- Cache hit rate

### View Metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name Requests \
  --dimensions Name=DistributionId,Value=$CF_DISTRIBUTION_ID \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Cost Considerations
- S3: $0.023/GB storage + $0.09/GB data transfer
- CloudFront: $0.085/GB data transfer (first 10TB)
- For low traffic: ~$5-10/month

## Cleanup Commands
```bash
# Delete CloudFront distribution
aws cloudfront get-distribution-config \
  --id $CF_DISTRIBUTION_ID \
  --query 'DistributionConfig' > /tmp/dist-config.json

# Disable distribution first
aws cloudfront update-distribution \
  --id $CF_DISTRIBUTION_ID \
  --if-match $(aws cloudfront get-distribution --id $CF_DISTRIBUTION_ID --query 'ETag' --output text) \
  --distribution-config file:///tmp/dist-config.json

# Wait for deployment
aws cloudfront wait distribution-deployed --id $CF_DISTRIBUTION_ID

# Delete distribution
aws cloudfront delete-distribution \
  --id $CF_DISTRIBUTION_ID \
  --if-match $(aws cloudfront get-distribution --id $CF_DISTRIBUTION_ID --query 'ETag' --output text)

# Delete OAI
aws cloudfront delete-cloud-front-origin-access-identity \
  --id $OAI_ID \
  --if-match $(aws cloudfront get-cloud-front-origin-access-identity --id $OAI_ID --query 'ETag' --output text)

# Empty and delete S3 bucket
aws s3 rm s3://$BUCKET_NAME --recursive --region ap-south-1
aws s3 rb s3://$BUCKET_NAME --region ap-south-1
```

## Next Steps
After completing this module:
- ✅ Frontend deployed globally via CloudFront
- ✅ HTTPS enabled by default
- ✅ Fast content delivery with CDN
- Ready for Module 8: DNS & SSL (Custom Domain)
