# Module 8: DNS & SSL (Custom Domain)

## Overview
Configure a custom domain with SSL certificate for your ecommerce application.

## Architecture
```
User → Route53 (DNS) → CloudFront (SSL) → S3 (Frontend)
                              ↓
                        API Gateway (Backend)
```

## Prerequisites
- A registered domain name (can register via Route53 or use existing)
- Completed Module 7 (CloudFront distribution)

## Resources to Create

### 1. Route53 Hosted Zone
- Domain: yourdomain.com
- Records: A record (alias to CloudFront)

### 2. ACM Certificate
- Domain: yourdomain.com, www.yourdomain.com
- Validation: DNS validation via Route53
- Region: us-east-1 (required for CloudFront)

### 3. Updated CloudFront Distribution
- Alternate domain names (CNAMEs)
- Custom SSL certificate

## Console Steps

### Step 1: Register Domain (if needed)

**Option A: Register via Route53**
1. Go to Route53 Console → Registered domains
2. Click "Register domain"
3. Search for available domain
4. Add to cart and complete registration
5. Wait for registration (can take up to 3 days, usually minutes)

**Option B: Use Existing Domain**
1. Update nameservers at your registrar to Route53 nameservers
2. Create hosted zone in Route53

### Step 2: Create Hosted Zone (if not auto-created)

1. Route53 Console → Hosted zones → Create hosted zone
2. Domain name: `yourdomain.com`
3. Type: Public hosted zone
4. Create
5. Note the 4 nameservers (NS records)
6. Update nameservers at your domain registrar

### Step 3: Request SSL Certificate in ACM

**IMPORTANT:** Certificate must be in us-east-1 region for CloudFront!

1. Go to ACM Console → **Switch to us-east-1 region**
2. Request certificate → Request a public certificate
3. Domain names:
   - `yourdomain.com`
   - `www.yourdomain.com`
   - `*.yourdomain.com` (optional, for subdomains)
4. Validation method: DNS validation
5. Key algorithm: RSA 2048
6. Request

### Step 4: Validate Certificate

1. In ACM, click on your certificate
2. Click "Create records in Route53" button
3. This automatically adds CNAME records to your hosted zone
4. Wait for validation (usually 5-30 minutes)
5. Status should change to "Issued"

### Step 5: Update CloudFront Distribution

1. CloudFront Console → Your distribution → Edit
2. Settings:
   - Alternate domain names (CNAMEs): Add `yourdomain.com` and `www.yourdomain.com`
   - Custom SSL certificate: Select your ACM certificate
3. Save changes
4. Wait for deployment (5-10 minutes)

### Step 6: Create Route53 Records

**A Record for root domain:**
1. Route53 → Hosted zones → Your domain
2. Create record:
   - Record name: Leave empty (root domain)
   - Record type: A
   - Alias: Yes
   - Route traffic to: Alias to CloudFront distribution
   - Choose distribution: Select your CloudFront distribution
   - Routing policy: Simple routing
3. Create record

**A Record for www:**
4. Create record:
   - Record name: `www`
   - Record type: A
   - Alias: Yes
   - Route traffic to: Alias to CloudFront distribution
   - Choose distribution: Select your CloudFront distribution
5. Create record

### Step 7: Update Cognito Callback URLs

1. Cognito Console → User pools → ecommerce-users
2. App integration → App client → Edit
3. Hosted UI settings:
   - Add callback URLs: `https://yourdomain.com`, `https://www.yourdomain.com`
   - Add sign-out URLs: `https://yourdomain.com`, `https://www.yourdomain.com`
4. Save

### Step 8: Update Frontend Configuration

1. Rebuild frontend with production domain:

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
          redirectSignIn: ['https://yourdomain.com'],
          redirectSignOut: ['https://yourdomain.com'],
          responseType: 'code'
        }
      }
    }
  }
};
```

2. Rebuild and deploy:
```bash
cd frontend/react-app
npm run build
aws s3 sync build/ s3://$BUCKET_NAME/ --delete
aws cloudfront create-invalidation --distribution-id $CF_DISTRIBUTION_ID --paths "/*"
```

### Step 9: Test Custom Domain

1. Open browser: `https://yourdomain.com`
2. Verify SSL certificate (should show valid)
3. Test all functionality:
   - Browse products
   - Sign in/Sign up
   - Add to cart
   - Place order

## CLI Commands

### Create Hosted Zone
```bash
DOMAIN_NAME="yourdomain.com"

HOSTED_ZONE_ID=$(aws route53 create-hosted-zone \
  --name $DOMAIN_NAME \
  --caller-reference $(date +%s) \
  --query 'HostedZone.Id' \
  --output text)

echo "HOSTED_ZONE_ID=$HOSTED_ZONE_ID" >> deployment/vpc-resources.txt
echo "Hosted Zone ID: $HOSTED_ZONE_ID"

# Get nameservers
aws route53 get-hosted-zone \
  --id $HOSTED_ZONE_ID \
  --query 'DelegationSet.NameServers' \
  --output table

echo "Update these nameservers at your domain registrar"
```

### Request ACM Certificate
```bash
# MUST be in us-east-1 for CloudFront
CERT_ARN=$(aws acm request-certificate \
  --domain-name $DOMAIN_NAME \
  --subject-alternative-names "www.$DOMAIN_NAME" "*.$DOMAIN_NAME" \
  --validation-method DNS \
  --region us-east-1 \
  --query 'CertificateArn' \
  --output text)

echo "CERT_ARN=$CERT_ARN" >> deployment/vpc-resources.txt
echo "Certificate ARN: $CERT_ARN"
```

### Get Validation Records
```bash
aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --region us-east-1 \
  --query 'Certificate.DomainValidationOptions[0].ResourceRecord' \
  --output table
```

### Create Validation Records in Route53
```bash
# Get validation record details
VALIDATION_NAME=$(aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --region us-east-1 \
  --query 'Certificate.DomainValidationOptions[0].ResourceRecord.Name' \
  --output text)

VALIDATION_VALUE=$(aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --region us-east-1 \
  --query 'Certificate.DomainValidationOptions[0].ResourceRecord.Value' \
  --output text)

# Create CNAME record for validation
cat > /tmp/validation-record.json <<EOF
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "$VALIDATION_NAME",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "$VALIDATION_VALUE"
          }
        ]
      }
    }
  ]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file:///tmp/validation-record.json

echo "Waiting for certificate validation..."
aws acm wait certificate-validated \
  --certificate-arn $CERT_ARN \
  --region us-east-1

echo "Certificate validated!"
```

### Update CloudFront Distribution
```bash
source deployment/vpc-resources.txt

# Get current distribution config
aws cloudfront get-distribution-config \
  --id $CF_DISTRIBUTION_ID \
  --query 'DistributionConfig' > /tmp/cf-config.json

# Update config with custom domain and certificate
# (Manual edit required - update Aliases and ViewerCertificate sections)

# Example updates needed in /tmp/cf-config.json:
# "Aliases": {
#   "Quantity": 2,
#   "Items": ["yourdomain.com", "www.yourdomain.com"]
# },
# "ViewerCertificate": {
#   "ACMCertificateArn": "$CERT_ARN",
#   "SSLSupportMethod": "sni-only",
#   "MinimumProtocolVersion": "TLSv1.2_2021"
# }

# Apply changes
ETAG=$(aws cloudfront get-distribution \
  --id $CF_DISTRIBUTION_ID \
  --query 'ETag' \
  --output text)

aws cloudfront update-distribution \
  --id $CF_DISTRIBUTION_ID \
  --if-match $ETAG \
  --distribution-config file:///tmp/cf-config.json

echo "Waiting for CloudFront deployment..."
aws cloudfront wait distribution-deployed \
  --id $CF_DISTRIBUTION_ID
```

### Create Route53 A Records
```bash
# Get CloudFront domain
CF_DOMAIN=$(aws cloudfront get-distribution \
  --id $CF_DISTRIBUTION_ID \
  --query 'Distribution.DomainName' \
  --output text)

# Get CloudFront hosted zone ID (always this value)
CF_HOSTED_ZONE_ID="Z2FDTNDATAQYW2"

# Create A record for root domain
cat > /tmp/root-record.json <<EOF
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "$DOMAIN_NAME",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "$CF_HOSTED_ZONE_ID",
          "DNSName": "$CF_DOMAIN",
          "EvaluateTargetHealth": false
        }
      }
    }
  ]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file:///tmp/root-record.json

# Create A record for www
cat > /tmp/www-record.json <<EOF
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.$DOMAIN_NAME",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "$CF_HOSTED_ZONE_ID",
          "DNSName": "$CF_DOMAIN",
          "EvaluateTargetHealth": false
        }
      }
    }
  ]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file:///tmp/www-record.json

echo "DNS records created!"
```

### Update Cognito Callback URLs
```bash
aws cognito-idp update-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-id $APP_CLIENT_ID \
  --callback-urls "http://localhost:3000" "https://$CF_DOMAIN" "https://$DOMAIN_NAME" "https://www.$DOMAIN_NAME" \
  --logout-urls "http://localhost:3000" "https://$CF_DOMAIN" "https://$DOMAIN_NAME" "https://www.$DOMAIN_NAME" \
  --region ap-south-1
```

## Verification

### Check DNS Propagation
```bash
# Check A record
dig $DOMAIN_NAME

# Check www
dig www.$DOMAIN_NAME

# Check nameservers
dig NS $DOMAIN_NAME
```

### Check SSL Certificate
```bash
# Check certificate
openssl s_client -connect $DOMAIN_NAME:443 -servername $DOMAIN_NAME < /dev/null

# Or use online tool: https://www.ssllabs.com/ssltest/
```

### Test Website
```bash
curl -I https://$DOMAIN_NAME
curl -I https://www.$DOMAIN_NAME
```

## Optional: Custom Domain for API Gateway

If you want a custom domain for your API (e.g., `api.yourdomain.com`):

### Create API Gateway Custom Domain

1. API Gateway Console → Custom domain names → Create
2. Domain name: `api.yourdomain.com`
3. ACM certificate: Select your wildcard certificate
4. Endpoint type: Regional
5. Create

### Add API Mapping

1. API mappings tab → Configure API mappings
2. API: ecommerce-api
3. Stage: $default
4. Path: Leave empty
5. Save

### Create Route53 Record

1. Route53 → Hosted zones → Your domain
2. Create record:
   - Name: `api`
   - Type: A
   - Alias: Yes
   - Route traffic to: Alias to API Gateway API
   - Choose API: Select your custom domain
3. Create

### Update Frontend
```javascript
const API_BASE_URL = 'https://api.yourdomain.com';
```

## Monitoring

### Route53 Query Metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Route53 \
  --metric-name QueryCount \
  --dimensions Name=HostedZoneId,Value=$HOSTED_ZONE_ID \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Cost Considerations
- Route53 Hosted Zone: $0.50/month
- Route53 Queries: $0.40 per million queries
- ACM Certificate: Free
- Domain registration: $12-15/year (varies by TLD)

## Cleanup Commands
```bash
# Delete Route53 records (except NS and SOA)
aws route53 list-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --query 'ResourceRecordSets[?Type!=`NS` && Type!=`SOA`]' \
  --output json > /tmp/records.json

# Delete each record (manual or script)

# Delete hosted zone
aws route53 delete-hosted-zone \
  --id $HOSTED_ZONE_ID

# Delete certificate
aws acm delete-certificate \
  --certificate-arn $CERT_ARN \
  --region us-east-1
```

## Final Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │ Route53 │ (yourdomain.com)
                    └────┬────┘
                         │
                  ┌──────▼──────┐
                  │ CloudFront  │ (SSL/CDN)
                  └──────┬──────┘
                         │
            ┌────────────┴────────────┐
            │                         │
       ┌────▼────┐              ┌────▼────────┐
       │   S3    │              │ API Gateway │
       │Frontend │              │   (JWT)     │
       └─────────┘              └────┬────────┘
                                     │
                              ┌──────▼──────┐
                              │     ALB     │
                              └──────┬──────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
              ┌─────▼─────┐    ┌────▼────┐    ┌─────▼─────┐
              │    ECS    │    │   ECS   │    │    ECS    │
              │ Services  │    │Services │    │ Services  │
              └─────┬─────┘    └────┬────┘    └─────┬─────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                              ┌─────▼─────┐
                              │    RDS    │
                              │PostgreSQL │
                              └───────────┘
```

## Congratulations! 🎉

You've successfully deployed a production-ready ecommerce application on AWS with:
- ✅ Custom domain with SSL
- ✅ Global CDN (CloudFront)
- ✅ Microservices architecture (ECS)
- ✅ API Gateway with authentication
- ✅ Event-driven notifications (SNS/SQS)
- ✅ Managed database (RDS)
- ✅ User authentication (Cognito)
- ✅ Secure networking (VPC)

## Next Steps
- Set up CI/CD pipeline (CodePipeline, GitHub Actions)
- Add monitoring and alerting (CloudWatch, X-Ray)
- Implement auto-scaling for ECS services
- Add WAF for security
- Set up backup and disaster recovery
- Optimize costs with Reserved Instances/Savings Plans
