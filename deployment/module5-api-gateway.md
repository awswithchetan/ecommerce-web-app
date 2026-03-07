# Module 5: API Gateway

## Overview
Create an API Gateway to provide a unified entry point for all microservices with Cognito authentication.

## Architecture
```
API Gateway (HTTP API)
├── Cognito Authorizer
├── VPC Link → ALB (private)
└── Routes:
    ├── GET /products → ALB/api/products
    ├── GET /cart → ALB/api/cart (authenticated)
    ├── POST /orders → ALB/api/orders (authenticated)
    └── GET /users/profile → ALB/api/users/profile (authenticated)
```

## Why API Gateway?
- Single entry point for all APIs
- Built-in authentication with Cognito
- Request/response transformation
- Rate limiting and throttling
- API versioning
- Monitoring and logging

## Resources to Create

### 1. VPC Link
- Connects API Gateway to private ALB
- Name: ecommerce-vpc-link

### 2. HTTP API
- Name: ecommerce-api
- Protocol: HTTP
- CORS: Enabled

### 3. Cognito Authorizer
- Type: JWT
- Identity source: $request.header.Authorization
- Audience: Cognito App Client ID

### 4. Routes
- Public routes (no auth): GET /products, GET /products/{id}
- Authenticated routes: /cart/*, /orders/*, /users/*

## Console Steps

### Step 1: Create VPC Link

1. Go to API Gateway Console → VPC Links
2. Click "Create"
3. VPC link version: VPC link for HTTP APIs
4. Name: `ecommerce-vpc-link`
5. VPC: ecommerce-vpc
6. Subnets: Select both private subnets
7. Security groups: Select ECS security group
8. Create (takes 5-10 minutes)

### Step 2: Create HTTP API

1. API Gateway Console → APIs → Create API
2. Choose: HTTP API → Build
3. Integrations:
   - Add integration: Private resource
   - Integration type: Application Load Balancer
   - VPC link: ecommerce-vpc-link
   - Load balancer: ecommerce-alb
   - Listener: HTTP 80
4. API name: `ecommerce-api`
5. Next

**Configure routes:**
6. Skip for now (we'll add manually)
7. Next

**Configure stages:**
8. Stage name: $default (auto-deploy)
9. Next

10. Review and Create

### Step 3: Configure CORS

1. Go to your API → CORS
2. Configure:
   - Access-Control-Allow-Origin: * (or specific domain)
   - Access-Control-Allow-Headers: content-type, x-user-id, authorization
   - Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
3. Save

### Step 4: Create Cognito Authorizer

1. API → Authorizers → Create
2. Authorizer type: JWT
3. Name: `cognito-authorizer`
4. Identity source: `$request.header.Authorization`
5. Issuer URL: `https://cognito-idp.ap-south-1.amazonaws.com/<user-pool-id>`
6. Audience: `<app-client-id>` (from Cognito)
7. Create

### Step 5: Create Integration

1. API → Integrations → Create
2. Attach this integration to a route: Skip
3. Integration type: Private resource
4. Integration details:
   - Target service: ALB/NLB
   - Load balancer: ecommerce-alb
   - Listener: HTTP 80
   - VPC link: ecommerce-vpc-link
5. Integration name: `alb-integration`
6. Create

### Step 6: Create Routes

**Public Routes (no auth):**

1. API → Routes → Create
2. Route: `GET /products`
3. Integration: alb-integration
4. Create

5. Route: `GET /products/{id}`
6. Integration: alb-integration
7. Create

**Authenticated Routes:**

8. Route: `GET /cart`
9. Integration: alb-integration
10. Authorization: cognito-authorizer
11. Create

12. Route: `POST /cart/items`
13. Integration: alb-integration
14. Authorization: cognito-authorizer
15. Create

16. Route: `DELETE /cart/items/{productId}`
17. Integration: alb-integration
18. Authorization: cognito-authorizer
19. Create

20. Route: `POST /orders`
21. Integration: alb-integration
22. Authorization: cognito-authorizer
23. Create

24. Route: `GET /orders`
25. Integration: alb-integration
26. Authorization: cognito-authorizer
27. Create

28. Route: `GET /users/profile`
29. Integration: alb-integration
30. Authorization: cognito-authorizer
31. Create

32. Route: `POST /users/profile`
33. Integration: alb-integration
34. Authorization: cognito-authorizer
35. Create

### Step 7: Note API Endpoint

1. Go to API → Stages → $default
2. Copy the Invoke URL (e.g., `https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com`)

## CLI Commands

### Create VPC Link
```bash
source deployment/vpc-resources.txt

VPC_LINK_ID=$(aws apigatewayv2 create-vpc-link \
  --name ecommerce-vpc-link \
  --subnet-ids $PRIVATE_SUBNET_1 $PRIVATE_SUBNET_2 \
  --security-group-ids $ECS_SG_ID \
  --region ap-south-1 \
  --query 'VpcLinkId' \
  --output text)

echo "VPC_LINK_ID=$VPC_LINK_ID" >> deployment/vpc-resources.txt
echo "Waiting for VPC Link to be available..."

# Wait for VPC Link to be available
aws apigatewayv2 get-vpc-link \
  --vpc-link-id $VPC_LINK_ID \
  --region ap-south-1 \
  --query 'VpcLinkStatus'
```

### Create HTTP API
```bash
API_ID=$(aws apigatewayv2 create-api \
  --name ecommerce-api \
  --protocol-type HTTP \
  --cors-configuration AllowOrigins='*',AllowMethods='GET,POST,PUT,DELETE,OPTIONS',AllowHeaders='content-type,x-user-id,authorization' \
  --region ap-south-1 \
  --query 'ApiId' \
  --output text)

echo "API_ID=$API_ID" >> deployment/vpc-resources.txt
echo "API ID: $API_ID"
```

### Create Cognito Authorizer
```bash
AUTHORIZER_ID=$(aws apigatewayv2 create-authorizer \
  --api-id $API_ID \
  --authorizer-type JWT \
  --name cognito-authorizer \
  --identity-source '$request.header.Authorization' \
  --jwt-configuration Audience=$APP_CLIENT_ID,Issuer=https://cognito-idp.ap-south-1.amazonaws.com/$USER_POOL_ID \
  --region ap-south-1 \
  --query 'AuthorizerId' \
  --output text)

echo "AUTHORIZER_ID=$AUTHORIZER_ID" >> deployment/vpc-resources.txt
```

### Create Integration
```bash
# Get ALB listener ARN
LISTENER_ARN=$(aws elbv2 describe-listeners \
  --load-balancer-arn $ALB_ARN \
  --region ap-south-1 \
  --query 'Listeners[0].ListenerArn' \
  --output text)

INTEGRATION_ID=$(aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type HTTP_PROXY \
  --integration-uri $LISTENER_ARN \
  --integration-method ANY \
  --connection-type VPC_LINK \
  --connection-id $VPC_LINK_ID \
  --payload-format-version 1.0 \
  --region ap-south-1 \
  --query 'IntegrationId' \
  --output text)

echo "INTEGRATION_ID=$INTEGRATION_ID" >> deployment/vpc-resources.txt
```

### Create Routes

```bash
# Public routes
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'GET /products' \
  --target integrations/$INTEGRATION_ID \
  --region ap-south-1

aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'GET /products/{id}' \
  --target integrations/$INTEGRATION_ID \
  --region ap-south-1

# Authenticated routes
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'GET /cart' \
  --target integrations/$INTEGRATION_ID \
  --authorization-type JWT \
  --authorizer-id $AUTHORIZER_ID \
  --region ap-south-1

aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'POST /cart/items' \
  --target integrations/$INTEGRATION_ID \
  --authorization-type JWT \
  --authorizer-id $AUTHORIZER_ID \
  --region ap-south-1

aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'DELETE /cart/items/{productId}' \
  --target integrations/$INTEGRATION_ID \
  --authorization-type JWT \
  --authorizer-id $AUTHORIZER_ID \
  --region ap-south-1

aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'POST /orders' \
  --target integrations/$INTEGRATION_ID \
  --authorization-type JWT \
  --authorizer-id $AUTHORIZER_ID \
  --region ap-south-1

aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'GET /orders' \
  --target integrations/$INTEGRATION_ID \
  --authorization-type JWT \
  --authorizer-id $AUTHORIZER_ID \
  --region ap-south-1

aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'GET /users/profile' \
  --target integrations/$INTEGRATION_ID \
  --authorization-type JWT \
  --authorizer-id $AUTHORIZER_ID \
  --region ap-south-1

aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'POST /users/profile' \
  --target integrations/$INTEGRATION_ID \
  --authorization-type JWT \
  --authorizer-id $AUTHORIZER_ID \
  --region ap-south-1
```

### Create Stage (Auto-deploy)
```bash
STAGE_ID=$(aws apigatewayv2 create-stage \
  --api-id $API_ID \
  --stage-name '$default' \
  --auto-deploy \
  --region ap-south-1 \
  --query 'StageName' \
  --output text)

# Get API endpoint
API_ENDPOINT=$(aws apigatewayv2 get-api \
  --api-id $API_ID \
  --region ap-south-1 \
  --query 'ApiEndpoint' \
  --output text)

echo "API_ENDPOINT=$API_ENDPOINT" >> deployment/vpc-resources.txt
echo "API Endpoint: $API_ENDPOINT"
```

## Update Frontend Configuration

Update `frontend/react-app/.env`:
```
REACT_APP_API_URL=https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com
```

Or update `src/api.js`:
```javascript
const API_BASE_URL = 'https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com';
```

## Testing

### Test Public Endpoint (No Auth)
```bash
curl https://<api-id>.execute-api.ap-south-1.amazonaws.com/products
```

### Test Authenticated Endpoint
```bash
# First, get a token from Cognito (use Hosted UI or SDK)
TOKEN="<your-jwt-token>"

curl -H "Authorization: Bearer $TOKEN" \
  https://<api-id>.execute-api.ap-south-1.amazonaws.com/cart
```

### Test from Frontend
Update your React app to use the new API Gateway endpoint and test authentication flow.

## Verification

### Check API Gateway
```bash
aws apigatewayv2 get-api \
  --api-id $API_ID \
  --region ap-south-1

aws apigatewayv2 get-routes \
  --api-id $API_ID \
  --region ap-south-1 \
  --query 'Items[].[RouteKey,AuthorizationType]' \
  --output table
```

### Check VPC Link Status
```bash
aws apigatewayv2 get-vpc-link \
  --vpc-link-id $VPC_LINK_ID \
  --region ap-south-1 \
  --query '[VpcLinkId,VpcLinkStatus,Name]' \
  --output table
```

## Monitoring

### Enable CloudWatch Logs
1. API Gateway Console → Your API → Stages → $default
2. Logs and tracing:
   - CloudWatch Logs: Enable
   - Log level: INFO
   - Log full requests/responses: Yes (for debugging)
3. Save

### View Logs
```bash
aws logs tail /aws/apigateway/ecommerce-api --follow --region ap-south-1
```

## Cost Considerations
- API Gateway HTTP API: $1.00 per million requests
- VPC Link: $0.01 per hour (~$7.20/month)
- Data transfer: $0.09/GB (first 10TB)
- For low traffic: ~$10-15/month

## Cleanup Commands
```bash
# Delete API
aws apigatewayv2 delete-api \
  --api-id $API_ID \
  --region ap-south-1

# Delete VPC Link
aws apigatewayv2 delete-vpc-link \
  --vpc-link-id $VPC_LINK_ID \
  --region ap-south-1
```

## Next Steps
After completing this module:
- ✅ API Gateway providing unified API endpoint
- ✅ Cognito authentication integrated
- ✅ VPC Link connecting to private ALB
- Ready for Module 6: Event-Driven Architecture (SNS/SQS)
