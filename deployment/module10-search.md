# Module 10: Search with OpenSearch

## Overview
Add full-text product search to the ecommerce application using Amazon OpenSearch Service. Product data is automatically synced from DynamoDB to OpenSearch via DynamoDB Streams and a Lambda indexer. Search requests are handled by a Lambda function sitting behind the existing internal ALB.

## What We'll Build
- **10.1** Amazon OpenSearch domain
- **10.2** IAM role for Lambda
- **10.3** Lambda deployment package
- **10.4** Lambda functions (search handler + DynamoDB indexer)
- **10.5** ALB Lambda target group and listener rule for `/search`
- **10.6** DynamoDB Stream to trigger the indexer
- **10.7** Bulk index existing products
- **10.8** Add API Gateway route for `/search`
- **10.9** Test search functionality

## Architecture
```
Browser → API Gateway → VPC Link → Internal ALB → /search* → Lambda (Search Handler)
                                                 → /products* → ECS Product Service

DynamoDB (products) → DynamoDB Stream → Lambda (Indexer) → OpenSearch
```

The search Lambda handles ALB requests directly. A separate Lambda indexer keeps OpenSearch in sync with DynamoDB changes in real time.

---

## 10.1 Create OpenSearch Domain

### Domain Configuration

1. **OpenSearch Console → Domains → Create domain**
2. **Domain name:** `ecommerce-search`
3. **Domain creation method:** Standard create
4. **Templates:** Dev/test
5. **Deployment option:** Domain without standby, 1 Availability Zone
6. **Engine version:** OpenSearch 2.x (latest)
7. **Instance type:** `t3.small.search`
8. **Number of nodes:** 1
9. **Storage:** EBS, 10 GB gp3

### Network Configuration
10. **Network:** VPC access
11. **VPC:** `ecommerce-vpc`
12. **Subnet:** Select one **private ECS subnet** (e.g., `ecommerce-private-ecs-1`)
13. **Security groups:** Create new security group:
    - **Name:** `ecommerce-opensearch-sg`
    - **Inbound:** HTTPS (443) from `ecommerce-ecs-sg` and from the Lambda security group (create below)
    - **Outbound:** All traffic

### Access Policy
14. **Access policy:** Only use fine-grained access control
15. **Fine-grained access control:** Enable
16. **Master user:** Create master user
    - **Username:** `admin`
    - **Password:** (create a strong password and save it)
17. **Create domain** (takes 10-15 minutes)

### Save These Values
- **Domain endpoint** (e.g., `https://search-ecommerce-search-xxxx.us-west-2.es.amazonaws.com`)

---

## 10.2 Create IAM Role for Lambda

### Create Lambda Security Group

1. **VPC Console → Security Groups → Create security group**
2. **Name:** `ecommerce-lambda-sg`
3. **VPC:** `ecommerce-vpc`
4. **Inbound rules:** None
5. **Outbound rules:** All traffic (Lambda needs to reach OpenSearch and DynamoDB)
6. **Create**

Then update `ecommerce-opensearch-sg` inbound rules to allow HTTPS (443) from `ecommerce-lambda-sg`.

### Create Lambda Execution Role

1. **IAM Console → Roles → Create role**
2. **Trusted entity:** AWS service → Lambda
3. **Attach policies:**
   - `AWSLambdaVPCAccessExecutionRole` (for VPC + CloudWatch Logs)
   - `AmazonDynamoDBReadOnlyAccess` (for stream access)
4. **Role name:** `ecommerce-lambda-search-role`
5. **Create role**

---

## 10.3 Create Lambda Deployment Package

The Lambda function requires `opensearch-py` and `requests-aws4auth` which are not available in the default Lambda runtime. Package them with the function code.

```bash
cd services/search-service

# Install dependencies into a package directory
pip install -r requirements.txt -t package/

# Copy function code
cp lambda_function.py package/

# Create zip
cd package
zip -r ../search-service.zip .
cd ..
```

This creates `services/search-service/search-service.zip`.

---

## 10.4 Create Lambda Functions

### 10.4.1 Search Handler Lambda (ALB)

1. **Lambda Console → Functions → Create function**
2. **Function name:** `ecommerce-search-handler`
3. **Runtime:** Python 3.11
4. **Architecture:** x86_64
5. **Execution role:** Use existing role → `ecommerce-lambda-search-role`
6. **Create function**

**Upload code:**
7. **Code tab → Upload from → .zip file**
8. **Upload** `search-service.zip`
9. **Handler:** `lambda_function.search_handler`

**Environment variables:**
10. **Configuration → Environment variables → Edit:**
    - `OPENSEARCH_ENDPOINT` = `<your-domain-endpoint-without-https>` (e.g., `search-ecommerce-search-xxxx.us-west-2.es.amazonaws.com`)
    - `AWS_REGION` = `<your-region>`

**VPC configuration:**
11. **Configuration → VPC → Edit:**
    - VPC: `ecommerce-vpc`
    - Subnets: Both private ECS subnets
    - Security groups: `ecommerce-lambda-sg`
12. **Save**

**Timeout:**
13. **Configuration → General configuration → Edit:**
    - Timeout: 30 seconds
14. **Save**

### 10.4.2 DynamoDB Indexer Lambda

1. **Create function**
2. **Function name:** `ecommerce-dynamodb-indexer`
3. **Runtime:** Python 3.11
4. **Execution role:** `ecommerce-lambda-search-role`
5. **Create function**
6. **Upload** same `search-service.zip`
7. **Handler:** `lambda_function.indexer_handler`
8. **Same environment variables and VPC configuration as above**

---

## 10.5 Add Lambda Target Group and ALB Listener Rule

### Create Lambda Target Group

1. **EC2 Console → Target Groups → Create target group**
2. **Target type:** Lambda function
3. **Target group name:** `ecommerce-search-tg`
4. **Register targets:** Select `ecommerce-search-handler`
5. **Create target group**

### Add ALB Listener Rule

1. **EC2 Console → Load Balancers → ecommerce-internal-alb**
2. **Listeners → HTTP:80 → View/edit rules**
3. **Add rule** (insert before the default rule):
   - **IF:** Path is `/search*`
   - **THEN:** Forward to `ecommerce-search-tg`
4. **Save**

---

## 10.6 Enable DynamoDB Stream

1. **DynamoDB Console → Tables → ecommerce-products**
2. **Exports and streams tab → DynamoDB stream details → Enable**
3. **View type:** New and old images
4. **Enable stream**

### Add Stream Trigger to Indexer Lambda

1. **Lambda Console → ecommerce-dynamodb-indexer → Configuration → Triggers → Add trigger**
2. **Source:** DynamoDB
3. **Table:** `ecommerce-products`
4. **Batch size:** 100
5. **Starting position:** Latest
6. **Add**

---

## 10.7 Bulk Index Existing Products

The DynamoDB Stream only captures changes going forward. Bulk index existing products using the AWS CLI:

```bash
# Export all products from DynamoDB
aws dynamodb scan \
  --table-name ecommerce-products \
  --region <your-region> \
  --output json | \
  python3 -c "
import json, sys, boto3

data = json.load(sys.stdin)
deserializer = boto3.dynamodb.types.TypeDeserializer()
products = [{k: deserializer.deserialize(v) for k, v in item.items()} for item in data['Items']]

# Build OpenSearch bulk request
bulk = ''
for p in products:
    bulk += json.dumps({'index': {'_index': 'products', '_id': p['product_id']}}) + '\n'
    bulk += json.dumps(p) + '\n'

with open('/tmp/bulk.json', 'w') as f:
    f.write(bulk)
print(f'Prepared {len(products)} products for indexing')
"

# Send bulk request to OpenSearch (run from within VPC or use a bastion host)
curl -X POST \
  "https://<opensearch-endpoint>/products/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  -u "admin:<password>" \
  --data-binary @/tmp/bulk.json
```

**Note:** The OpenSearch domain is in a private VPC subnet. Run the curl command from a bastion host or an EC2 instance in the same VPC.

---

## 10.8 Add API Gateway Route for `/search`

The existing API Gateway already routes all traffic through the ALB via VPC Link. Since the ALB now has a `/search*` rule, no new API Gateway integration is needed — just verify the existing `ANY /{proxy+}` route covers it.

**Test the route is reachable:**
```bash
curl "https://<api-gateway-url>/search?q=headphones"
```

If this returns a 401 (JWT required), add a dedicated public route for search:

1. **API Gateway Console → your API → Routes → Create route**
2. **Method:** GET
3. **Resource path:** `/search`
4. **Integration:** Select the existing ALB integration
5. **Authorization:** None (search is public)
6. **Create route**

---

## 10.9 Test Search

**Test via API Gateway:**
```bash
# Full-text search
curl "https://<api-gateway-url>/search?q=headphones"

# Category filter
curl "https://<api-gateway-url>/search?category=Electronics"

# Combined
curl "https://<api-gateway-url>/search?q=wireless&category=Electronics"
```

**Expected response:** JSON array of matching products, ranked by relevance.

**Test via frontend:**
1. Open your CloudFront URL
2. Type in the search bar on the Products page
3. Results should update with matched products

### Troubleshooting

**Lambda timeout / connection refused:**
- Verify Lambda VPC config uses private ECS subnets
- Confirm `ecommerce-opensearch-sg` allows HTTPS from `ecommerce-lambda-sg`
- Check Lambda CloudWatch logs: `/aws/lambda/ecommerce-search-handler`

**Empty search results after bulk index:**
- Verify the bulk index curl ran successfully (check for errors in response)
- Check OpenSearch index exists: `curl -u admin:<password> https://<endpoint>/products/_count`

**DynamoDB stream not triggering indexer:**
- Confirm stream is enabled on the products table
- Check Lambda trigger is in "Enabled" state
- Review indexer logs: `/aws/lambda/ecommerce-dynamodb-indexer`

## Next Steps
Proceed to **[Module 11: Cleanup](./module11-cleanup.md)** to remove all AWS resources.
