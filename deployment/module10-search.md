# Module 10: Search with OpenSearch

## Overview
Add full-text product search using Amazon OpenSearch Service. The search service runs as an ECS/Fargate container behind the existing internal ALB — same pattern as the other microservices. Product data is automatically synced to OpenSearch via DynamoDB Streams and a simple Lambda function (no packaging required).

## What We'll Build
- **10.1** Amazon OpenSearch domain
- **10.2** Search service — ECR, ECS task definition and service
- **10.3** ALB target group and listener rule for `/search`
- **10.4** Parameter Store configuration for OpenSearch
- **10.5** DynamoDB Stream → Lambda indexer (inline code, no packaging)
- **10.6** Bulk index existing products
- **10.7** Add API Gateway route for `/search`
- **10.8** Test search functionality

## Architecture
```
Browser → API Gateway → VPC Link → Internal ALB → /search* → ECS Search Service → OpenSearch
                                                 → /products* → ECS Product Service

DynamoDB (products) → DynamoDB Stream → Lambda (Indexer) → OpenSearch
```

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
13. **Security groups:** Create new:
    - **Name:** `ecommerce-opensearch-sg`
    - **Inbound:** HTTPS (443) from `ecommerce-ecs-sg` (ECS tasks can reach OpenSearch)
    - **Outbound:** All traffic

### Access Policy
14. **Access policy:** Only use fine-grained access control
15. **Fine-grained access control:** Enable
16. **Master user:** Create master user
    - **Username:** `admin`
    - **Password:** (create a strong password and save it)
17. **Create domain** — takes 10-15 minutes

### Save These Values
- **Domain endpoint** (e.g., `https://search-ecommerce-search-xxxx.us-west-2.es.amazonaws.com`)

---

## 10.2 Deploy Search Service to ECS

### 10.2.1 Create ECR Repository

1. **ECR Console → Repositories → Create repository**
2. **Repository name:** `ecommerce/search-service`
3. **Create repository**

### 10.2.2 Build and Push Docker Image

```bash
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<your-region>.amazonaws.com

cd services/search-service
docker build -t ecommerce/search-service .
docker tag ecommerce/search-service:latest <account-id>.dkr.ecr.<your-region>.amazonaws.com/ecommerce/search-service:latest
docker push <account-id>.dkr.ecr.<your-region>.amazonaws.com/ecommerce/search-service:latest
```

### 10.2.3 Create Target Group

1. **EC2 Console → Target Groups → Create target group**
2. **Target type:** IP addresses
3. **Target group name:** `ecommerce-search-tg`
4. **Protocol:** HTTP, Port: **8005**
5. **VPC:** `ecommerce-vpc`
6. **Health check path:** `/health`
7. **Create target group**

### 10.2.4 Add ALB Listener Rule

1. **EC2 Console → Load Balancers → ecommerce-internal-alb**
2. **Listeners → HTTP:80 → View/edit rules → Add rule:**
   - **IF:** Path is `/search*`
   - **THEN:** Forward to `ecommerce-search-tg`
3. **Save**

### 10.2.5 Create ECS Task Definition

1. **ECS Console → Task definitions → Create new task definition**
2. **Task definition family:** `ecommerce-search-service`
3. **Launch type:** AWS Fargate
4. **Operating system:** Linux/X86_64
5. **CPU:** 0.25 vCPU, **Memory:** 0.5 GB
6. **Task role:** `ecommerce-ecs-task-role`
7. **Task execution role:** `ecsTaskExecutionRole`
8. **Container:**
   - **Name:** `search-service`
   - **Image URI:** `<account-id>.dkr.ecr.<your-region>.amazonaws.com/ecommerce/search-service:latest`
   - **Port:** 8005
   - **Environment variables:**
     - `ENVIRONMENT` = `dev`
     - `AWS_REGION` = `<your-region>`
   - **Log configuration:** awslogs, log group `/ecs/ecommerce-search-service`
9. **Create task definition**

### 10.2.6 Create ECS Service

1. **ECS Console → Clusters → ecommerce-cluster → Services → Create**
2. **Launch type:** Fargate
3. **Task definition:** `ecommerce-search-service:1`
4. **Service name:** `ecommerce-search-service`
5. **Desired tasks:** 1
6. **VPC:** `ecommerce-vpc`
7. **Subnets:** Both private ECS subnets
8. **Security group:** `ecommerce-ecs-sg`
9. **Public IP:** Disabled
10. **Load balancing:** Application Load Balancer → `ecommerce-internal-alb`
11. **Target group:** `ecommerce-search-tg`
12. **Create service**

---

## 10.3 Add Parameter Store Configuration

1. **Systems Manager Console → Parameter Store → Create parameter**

**OpenSearch Endpoint:**
- **Name:** `/ecommerce/dev/opensearch/endpoint`
- **Type:** String
- **Value:** `https://<your-opensearch-domain-endpoint>`

**OpenSearch Username:**
- **Name:** `/ecommerce/dev/opensearch/username`
- **Type:** String
- **Value:** `admin`

**OpenSearch Password:**
- **Name:** `/ecommerce/dev/opensearch/password`
- **Type:** SecureString
- **Value:** `<your-opensearch-master-password>`

---

## 10.4 DynamoDB Stream → Lambda Indexer

### Create Lambda Function

1. **Lambda Console → Functions → Create function**
2. **Function name:** `ecommerce-dynamodb-indexer`
3. **Runtime:** Python 3.11
4. **Execution role:** Create new role with basic Lambda permissions
   - After creation, attach `AmazonDynamoDBReadOnlyAccess` to the role
5. **Create function**

### Paste Inline Code

6. **Code tab → Edit inline**
7. **Copy and paste the contents of `services/search-service/dynamodb_indexer.py`**
8. **Deploy**

### Set Environment Variables

9. **Configuration → Environment variables → Edit:**
   - `OPENSEARCH_ENDPOINT` = `https://<your-opensearch-domain-endpoint>`
   - `OPENSEARCH_USERNAME` = `admin`
   - `OPENSEARCH_PASSWORD` = `<your-master-password>`

### Enable DynamoDB Stream

10. **DynamoDB Console → Tables → ecommerce-products**
11. **Exports and streams tab → DynamoDB stream details → Enable**
12. **View type:** New and old images
13. **Enable stream**

### Add Stream Trigger

14. **Lambda Console → ecommerce-dynamodb-indexer → Configuration → Triggers → Add trigger**
15. **Source:** DynamoDB
16. **Table:** `ecommerce-products`
17. **Batch size:** 100
18. **Starting position:** Latest
19. **Add**

---

## 10.5 Bulk Index Existing Products

The DynamoDB Stream only captures changes going forward. Run this script to index all existing products.

**Run from a bastion host or any machine with VPC access:**

```bash
# Export products from DynamoDB and bulk index into OpenSearch
python3 << 'EOF'
import boto3, json, urllib.request, urllib.error, base64

REGION = '<your-region>'
OPENSEARCH_ENDPOINT = 'https://<your-opensearch-endpoint>'
USERNAME = 'admin'
PASSWORD = '<your-password>'
INDEX = 'products'

# Fetch all products from DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table('ecommerce-products')
products = table.scan()['Items']

# Build bulk request body
bulk = ''
for p in products:
    bulk += json.dumps({'index': {'_index': INDEX, '_id': p['product_id']}}) + '\n'
    bulk += json.dumps(p) + '\n'

# Send to OpenSearch
auth = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
req = urllib.request.Request(
    f"{OPENSEARCH_ENDPOINT}/{INDEX}/_bulk",
    data=bulk.encode(),
    method='POST',
    headers={'Content-Type': 'application/x-ndjson', 'Authorization': f'Basic {auth}'}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    errors = [i for i in result.get('items', []) if 'error' in i.get('index', {})]
    print(f"Indexed {len(products)} products. Errors: {len(errors)}")
EOF
```

---

## 10.6 Add API Gateway Route for `/search`

The existing `ANY /{proxy+}` route requires JWT authentication. Add a dedicated public route for search:

1. **API Gateway Console → your API → Routes → Create route**
2. **Method:** GET
3. **Resource path:** `/search`
4. **Integration:** Select the existing ALB integration
5. **Authorization:** None (search is public)
6. **Create route**

---

## 10.7 Test Search

**Test via API Gateway:**
```bash
# Full-text search
curl "https://<api-gateway-url>/search?q=headphones"

# Category filter
curl "https://<api-gateway-url>/search?category=Electronics"

# Combined
curl "https://<api-gateway-url>/search?q=wireless&category=Electronics"
```

**Test via frontend:**
1. Open your CloudFront URL
2. Type in the search bar on the Products page
3. Results update with matched products ranked by relevance

### Troubleshooting

**Empty search results:**
- Verify bulk index ran successfully
- Check ECS search service logs in CloudWatch: `/ecs/ecommerce-search-service`
- Confirm `ecommerce-opensearch-sg` allows HTTPS (443) from `ecommerce-ecs-sg`

**DynamoDB stream not triggering indexer:**
- Confirm stream is enabled on the products table
- Check Lambda trigger is in "Enabled" state
- Review Lambda logs: `/aws/lambda/ecommerce-dynamodb-indexer`

**Search service not starting:**
- Verify Parameter Store values are correct
- Check ECS task has `ecommerce-ecs-task-role` with `AmazonSSMReadOnlyAccess`

## Next Steps
Proceed to **[Module 11: Cleanup](./module11-cleanup.md)** to remove all AWS resources.
