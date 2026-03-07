# Module 6: Event-Driven Architecture (SNS/SQS/SES)

## Overview
Implement asynchronous order processing and email notifications using SNS, SQS, and SES.

## Architecture
```
Order Service
    ↓ (publishes event)
SNS Topic: order-events
    ↓ (fan-out)
    ├→ SQS Queue: order-notifications
    │      ↓
    │  Notification Service (polls queue)
    │      ↓
    │  SES (sends email)
    │
    └→ (Future: Analytics, Inventory, etc.)
```

## Why Event-Driven?
- Decoupling: Services don't need to know about each other
- Scalability: Handle traffic spikes with queues
- Reliability: Messages persist in queue if service is down
- Fan-out: One event can trigger multiple actions

## Resources to Create

### 1. SNS Topic
- Name: order-events
- Type: Standard
- Encryption: Enabled

### 2. SQS Queue
- Name: order-notifications
- Type: Standard
- Visibility timeout: 30 seconds
- Message retention: 4 days
- Dead letter queue: order-notifications-dlq

### 3. Dead Letter Queue
- Name: order-notifications-dlq
- For failed message processing

### 4. SES Configuration
- Verify email address (for sending)
- Verify domain (optional, for production)

### 5. IAM Roles
- ECS Task Role: Allow SNS publish, SQS receive, SES send

## Console Steps

### Step 1: Create SNS Topic

1. Go to SNS Console → Topics → Create topic
2. Type: Standard
3. Name: `order-events`
4. Display name: Order Events
5. Encryption: Enable (use default KMS key)
6. Access policy: Default (we'll update later)
7. Create topic
8. Note the Topic ARN

### Step 2: Create Dead Letter Queue

1. Go to SQS Console → Create queue
2. Type: Standard
3. Name: `order-notifications-dlq`
4. Configuration: Keep defaults
5. Create queue

### Step 3: Create Main SQS Queue

1. SQS Console → Create queue
2. Type: Standard
3. Name: `order-notifications`
4. Configuration:
   - Visibility timeout: 30 seconds
   - Message retention period: 4 days
   - Delivery delay: 0 seconds
   - Maximum message size: 256 KB
   - Receive message wait time: 0 seconds (short polling)
5. Dead-letter queue:
   - Enable
   - Choose: order-notifications-dlq
   - Maximum receives: 3
6. Encryption: Enable (use default KMS key)
7. Create queue
8. Note the Queue URL and ARN

### Step 4: Subscribe Queue to SNS Topic

1. Go to SNS Console → Topics → order-events
2. Create subscription:
   - Protocol: Amazon SQS
   - Endpoint: Select order-notifications queue ARN
   - Enable raw message delivery: No
3. Create subscription

### Step 5: Update Queue Access Policy

1. Go to SQS Console → order-notifications → Access policy
2. Edit policy to allow SNS to send messages:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sns.amazonaws.com"
      },
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:ap-south-1:<account-id>:order-notifications",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "arn:aws:sns:ap-south-1:<account-id>:order-events"
        }
      }
    }
  ]
}
```

### Step 6: Verify Email in SES

1. Go to SES Console → Verified identities
2. Create identity:
   - Identity type: Email address
   - Email address: your-email@example.com
3. Create identity
4. Check your email and click verification link
5. Status should change to "Verified"

**Note:** In sandbox mode, you can only send to verified addresses. To send to any address, request production access.

### Step 7: Create IAM Policy for ECS Tasks

1. IAM Console → Policies → Create policy
2. JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:ap-south-1:<account-id>:order-events"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:ap-south-1:<account-id>:order-notifications"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

3. Name: `ecommerce-ecs-task-policy`
4. Create policy

### Step 8: Create ECS Task Role

1. IAM Console → Roles → Create role
2. Trusted entity: ECS Task
3. Permissions:
   - Attach: ecommerce-ecs-task-policy
4. Role name: `ecommerce-ecs-task-role`
5. Create role

### Step 9: Update ECS Task Definitions

Update task definitions to include:
- Task role: ecommerce-ecs-task-role
- Environment variables:
  - SNS_TOPIC_ARN: (order-events ARN)
  - SQS_QUEUE_URL: (order-notifications URL)
  - SES_FROM_EMAIL: (verified email)

### Step 10: Update and Redeploy Services

1. Update order-service task definition with SNS topic ARN
2. Update notification-service task definition with SQS queue URL and SES email
3. Update ECS services to use new task definitions

## CLI Commands

### Create SNS Topic
```bash
SNS_TOPIC_ARN=$(aws sns create-topic \
  --name order-events \
  --attributes DisplayName="Order Events" \
  --region ap-south-1 \
  --query 'TopicArn' \
  --output text)

echo "SNS_TOPIC_ARN=$SNS_TOPIC_ARN" >> deployment/vpc-resources.txt
echo "SNS Topic ARN: $SNS_TOPIC_ARN"
```

### Create Dead Letter Queue
```bash
DLQ_URL=$(aws sqs create-queue \
  --queue-name order-notifications-dlq \
  --region ap-south-1 \
  --query 'QueueUrl' \
  --output text)

DLQ_ARN=$(aws sqs get-queue-attributes \
  --queue-url $DLQ_URL \
  --attribute-names QueueArn \
  --region ap-south-1 \
  --query 'Attributes.QueueArn' \
  --output text)

echo "DLQ_URL=$DLQ_URL" >> deployment/vpc-resources.txt
echo "DLQ_ARN=$DLQ_ARN" >> deployment/vpc-resources.txt
```

### Create Main Queue
```bash
QUEUE_URL=$(aws sqs create-queue \
  --queue-name order-notifications \
  --attributes VisibilityTimeout=30,MessageRetentionPeriod=345600,RedrivePolicy="{\"deadLetterTargetArn\":\"$DLQ_ARN\",\"maxReceiveCount\":\"3\"}" \
  --region ap-south-1 \
  --query 'QueueUrl' \
  --output text)

QUEUE_ARN=$(aws sqs get-queue-attributes \
  --queue-url $QUEUE_URL \
  --attribute-names QueueArn \
  --region ap-south-1 \
  --query 'Attributes.QueueArn' \
  --output text)

echo "QUEUE_URL=$QUEUE_URL" >> deployment/vpc-resources.txt
echo "QUEUE_ARN=$QUEUE_ARN" >> deployment/vpc-resources.txt
echo "Queue URL: $QUEUE_URL"
```

### Subscribe Queue to SNS
```bash
SUBSCRIPTION_ARN=$(aws sns subscribe \
  --topic-arn $SNS_TOPIC_ARN \
  --protocol sqs \
  --notification-endpoint $QUEUE_ARN \
  --region ap-south-1 \
  --query 'SubscriptionArn' \
  --output text)

echo "Subscription ARN: $SUBSCRIPTION_ARN"
```

### Update Queue Policy
```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cat > /tmp/queue-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sns.amazonaws.com"
      },
      "Action": "sqs:SendMessage",
      "Resource": "$QUEUE_ARN",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "$SNS_TOPIC_ARN"
        }
      }
    }
  ]
}
EOF

aws sqs set-queue-attributes \
  --queue-url $QUEUE_URL \
  --attributes file:///tmp/queue-policy.json \
  --region ap-south-1
```

### Verify Email in SES
```bash
aws ses verify-email-identity \
  --email-address your-email@example.com \
  --region ap-south-1

echo "Check your email and click the verification link"
```

### Check Email Verification Status
```bash
aws ses get-identity-verification-attributes \
  --identities your-email@example.com \
  --region ap-south-1
```

### Create IAM Policy
```bash
cat > /tmp/ecs-task-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["sns:Publish"],
      "Resource": "$SNS_TOPIC_ARN"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "$QUEUE_ARN"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
EOF

POLICY_ARN=$(aws iam create-policy \
  --policy-name ecommerce-ecs-task-policy \
  --policy-document file:///tmp/ecs-task-policy.json \
  --query 'Policy.Arn' \
  --output text)

echo "POLICY_ARN=$POLICY_ARN" >> deployment/vpc-resources.txt
```

### Create ECS Task Role
```bash
cat > /tmp/ecs-task-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

TASK_ROLE_ARN=$(aws iam create-role \
  --role-name ecommerce-ecs-task-role \
  --assume-role-policy-document file:///tmp/ecs-task-trust-policy.json \
  --query 'Role.Arn' \
  --output text)

aws iam attach-role-policy \
  --role-name ecommerce-ecs-task-role \
  --policy-arn $POLICY_ARN

echo "TASK_ROLE_ARN=$TASK_ROLE_ARN" >> deployment/vpc-resources.txt
echo "Task Role ARN: $TASK_ROLE_ARN"
```

## Update Service Code

### Order Service Environment Variables
Add to task definition:
```json
{
  "name": "SNS_TOPIC_ARN",
  "value": "arn:aws:sns:ap-south-1:<account-id>:order-events"
},
{
  "name": "AWS_REGION",
  "value": "ap-south-1"
}
```

### Notification Service Environment Variables
Add to task definition:
```json
{
  "name": "SQS_QUEUE_URL",
  "value": "https://sqs.ap-south-1.amazonaws.com/<account-id>/order-notifications"
},
{
  "name": "SES_FROM_EMAIL",
  "value": "your-verified-email@example.com"
},
{
  "name": "AWS_REGION",
  "value": "ap-south-1"
}
```

## Testing

### Test SNS Publishing
```bash
aws sns publish \
  --topic-arn $SNS_TOPIC_ARN \
  --message '{"order_id": 123, "user_email": "test@example.com", "total_amount": 99.99}' \
  --region ap-south-1
```

### Check Messages in Queue
```bash
aws sqs receive-message \
  --queue-url $QUEUE_URL \
  --max-number-of-messages 1 \
  --region ap-south-1
```

### Test SES Email
```bash
aws ses send-email \
  --from your-verified-email@example.com \
  --destination ToAddresses=your-verified-email@example.com \
  --message Subject={Data="Test Email"},Body={Text={Data="This is a test"}} \
  --region ap-south-1
```

### End-to-End Test
1. Create an order through the frontend
2. Check CloudWatch Logs for order-service (should see SNS publish)
3. Check SQS queue for message
4. Check CloudWatch Logs for notification-service (should see message processing)
5. Check your email for order confirmation

## Monitoring

### CloudWatch Metrics
- SNS: NumberOfMessagesPublished, NumberOfNotificationsFailed
- SQS: NumberOfMessagesSent, NumberOfMessagesReceived, ApproximateAgeOfOldestMessage
- SES: Send, Delivery, Bounce, Complaint

### View Metrics
```bash
# SNS metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/SNS \
  --metric-name NumberOfMessagesPublished \
  --dimensions Name=TopicName,Value=order-events \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum \
  --region ap-south-1
```

## Cost Considerations
- SNS: $0.50 per million requests (first million free)
- SQS: $0.40 per million requests (first million free)
- SES: $0.10 per 1,000 emails (sandbox: 200/day free)
- For low traffic: Essentially free

## Cleanup Commands
```bash
# Delete subscription
aws sns unsubscribe \
  --subscription-arn $SUBSCRIPTION_ARN \
  --region ap-south-1

# Delete SNS topic
aws sns delete-topic \
  --topic-arn $SNS_TOPIC_ARN \
  --region ap-south-1

# Delete queues
aws sqs delete-queue \
  --queue-url $QUEUE_URL \
  --region ap-south-1

aws sqs delete-queue \
  --queue-url $DLQ_URL \
  --region ap-south-1

# Delete IAM resources
aws iam detach-role-policy \
  --role-name ecommerce-ecs-task-role \
  --policy-arn $POLICY_ARN

aws iam delete-role \
  --role-name ecommerce-ecs-task-role

aws iam delete-policy \
  --policy-arn $POLICY_ARN
```

## Next Steps
After completing this module:
- ✅ Event-driven architecture implemented
- ✅ Order notifications sent via email
- ✅ Scalable and decoupled services
- Ready for Module 7: Frontend Deployment (S3/CloudFront)
