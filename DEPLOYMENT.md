# Deployment Guide

This guide provides step-by-step instructions for deploying the AI Sales Helper platform to AWS.

## Prerequisites

Before starting, ensure you have:

- AWS Account with administrator access
- AWS CLI configured (`aws configure`)
- Terraform 1.6+ installed
- Node.js 18+ installed
- Python 3.11+ installed
- OpenAI API key
- Telegram bot token from @BotFather

## Deployment Steps

### Step 1: Prepare AWS Account

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Create Terraform state bucket
aws s3 mb s3://salesai-terraform-state --region us-east-1
```

### Step 2: Configure Terraform

```bash
cd terraform

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
# IMPORTANT: Use strong passwords and keep secret keys secure
nano terraform.tfvars
```

Required variables:
```hcl
project_name = "salesai"
environment  = "prod"
aws_region   = "us-east-1"

db_username = "salesai_admin"
db_password = "CHANGE-TO-STRONG-PASSWORD"

openai_api_key     = "sk-your-openai-api-key-here"
telegram_bot_token = "your-telegram-bot-token"
secret_key         = "generate-a-strong-random-key"
```

### Step 3: Build Backend Package

```bash
cd ../backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create Lambda package
mkdir -p lambda-package
pip install -r requirements.txt -t lambda-package/ --platform manylinux2014_x86_64 --only-binary=:all:
cp -r app lambda-package/
cp lambda_handler.py lambda-package/

# Create zip file
cd lambda-package
zip -r ../lambda-package.zip . -x "*.pyc" "**/__pycache__/*"
cd ..
```

### Step 4: Deploy Infrastructure

```bash
cd ../terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Deploy (this will take 10-15 minutes)
terraform apply

# Save the outputs
terraform output -json > outputs.json
```

**Important outputs:**
- `api_gateway_url` - Your API endpoint
- `frontend_url` - CloudFront URL for dashboard
- `telegram_webhook_url` - Webhook for Telegram
- `rds_endpoint` - Database endpoint

### Step 5: Run Database Migrations

```bash
cd ../backend

# Set DATABASE_URL from Terraform output
export DATABASE_URL="postgresql://username:password@rds-endpoint:5432/salesai"

# Run migrations (if using Alembic)
alembic upgrade head
```

### Step 6: Build and Deploy Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Create production .env
cat > .env << EOF
VITE_API_URL=https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/api
EOF

# Build
npm run build

# Deploy to S3
aws s3 sync dist/ s3://salesai-frontend-ACCOUNT_ID/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

### Step 7: Set Up GitHub Actions (Optional)

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
DB_PASSWORD=your-db-password
OPENAI_API_KEY=sk-your-key
TELEGRAM_BOT_TOKEN=your-bot-token
SECRET_KEY=your-jwt-secret
API_URL=https://your-api-gateway-url
S3_FRONTEND_BUCKET=salesai-frontend-ACCOUNT_ID
CLOUDFRONT_DISTRIBUTION_ID=E1234567890ABC
```

Now pushes to main will automatically deploy.

### Step 8: Configure Telegram Bot

1. Access your dashboard at the CloudFront URL
2. Register an account
3. Go to Settings
4. Enter your Telegram bot token
5. Click "Save Bot Configuration"

The webhook will be automatically registered with Telegram.

### Step 9: Test the System

**Test the Dashboard:**
1. Log in to the dashboard
2. Create a product with images
3. Add a discount rule
4. Verify the product appears correctly

**Test the Telegram Bot:**
1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Try browsing products
5. Test placing an order

### Step 10: Monitor the Deployment

**Check Lambda logs:**
```bash
aws logs tail /aws/lambda/salesai-api --follow
```

**Check API Gateway:**
```bash
aws logs tail /aws/apigateway/salesai --follow
```

**Check RDS:**
```bash
aws rds describe-db-instances --db-instance-identifier salesai-db
```

## Post-Deployment Configuration

### Set Up CloudWatch Alarms

```bash
# Create alarm for Lambda errors
aws cloudwatch put-metric-alarm \
  --alarm-name salesai-lambda-errors \
  --alarm-description "Alert when Lambda has errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1

# Create alarm for RDS CPU
aws cloudwatch put-metric-alarm \
  --alarm-name salesai-rds-cpu \
  --alarm-description "Alert when RDS CPU is high" \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### Configure Backup

```bash
# Verify RDS automated backups
aws rds describe-db-instances \
  --db-instance-identifier salesai-db \
  --query 'DBInstances[0].BackupRetentionPeriod'
```

### Set Up Custom Domain (Optional)

1. Register domain in Route 53
2. Request ACM certificate in us-east-1
3. Update CloudFront distribution
4. Update terraform.tfvars with domain
5. Run `terraform apply` again

## Updating the Application

### Update Backend

```bash
# Make changes to backend code
cd backend

# Rebuild Lambda package
./build-lambda.sh  # Or manual steps from above

# Deploy with Terraform
cd ../terraform
terraform apply -target=aws_lambda_function.api
```

Or simply push to main and GitHub Actions will deploy.

### Update Frontend

```bash
cd frontend

# Make changes to frontend code
npm run build

# Deploy
aws s3 sync dist/ s3://your-frontend-bucket/ --delete
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

## Rollback Procedure

If something goes wrong:

### Rollback Lambda

```bash
# List function versions
aws lambda list-versions-by-function --function-name salesai-api

# Rollback to previous version
aws lambda update-alias \
  --function-name salesai-api \
  --name LIVE \
  --function-version <previous-version>
```

### Rollback Frontend

```bash
# Frontend is versioned in Git
git checkout <previous-commit>
cd frontend
npm run build
aws s3 sync dist/ s3://your-bucket/ --delete
```

### Rollback Terraform

```bash
cd terraform
git checkout <previous-commit>
terraform apply
```

## Disaster Recovery

### Database Backup

```bash
# Manual backup
aws rds create-db-snapshot \
  --db-instance-identifier salesai-db \
  --db-snapshot-identifier salesai-backup-$(date +%Y%m%d)

# Restore from backup
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier salesai-db-restored \
  --db-snapshot-identifier salesai-backup-20240101
```

### Complete System Restore

1. Restore RDS from snapshot
2. Update DATABASE_URL in Secrets Manager
3. Redeploy Lambda function
4. Verify connectivity

## Troubleshooting

### Lambda Can't Connect to RDS

**Check:**
- Lambda is in the correct VPC subnets
- Security groups allow Lambda → RDS on port 5432
- NAT Gateway is configured and routes are correct
- DATABASE_URL environment variable is correct

```bash
# Test from Lambda
aws lambda invoke \
  --function-name salesai-api \
  --payload '{"httpMethod":"GET","path":"/health"}' \
  response.json
```

### Telegram Webhook Fails

**Check:**
- API Gateway URL is publicly accessible
- Bot token is correct in environment variables
- Check Lambda logs for errors

```bash
# Check webhook status
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### Frontend Not Loading

**Check:**
- S3 bucket policy allows public read
- CloudFront distribution is enabled
- VITE_API_URL is correct in build

```bash
# Check S3 bucket contents
aws s3 ls s3://your-frontend-bucket/

# Check CloudFront status
aws cloudfront get-distribution --id YOUR_ID
```

## Cost Optimization

### For Development

- Use db.t3.micro for RDS (included in free tier)
- Disable NAT Gateway (use VPC endpoints instead)
- Use Lambda free tier (1M requests/month)

### For Production

- Enable RDS auto-scaling
- Use CloudFront caching effectively
- Implement API response caching
- Consider Reserved Instances for predictable load

## Security Checklist

- [ ] Changed all default passwords
- [ ] Enabled MFA on AWS account
- [ ] Secrets stored in Secrets Manager
- [ ] RDS in private subnet
- [ ] Security groups follow least privilege
- [ ] HTTPS enforced
- [ ] Regular security updates
- [ ] CloudWatch alarms configured
- [ ] Backup strategy in place
- [ ] IAM roles follow least privilege

## Monitoring Checklist

- [ ] CloudWatch dashboards created
- [ ] Log retention configured
- [ ] Alarms for errors set up
- [ ] Performance metrics tracked
- [ ] Cost alerts configured
- [ ] Backup alerts enabled

## Support

If you encounter issues during deployment:

1. Check AWS CloudWatch logs
2. Review Terraform plan output
3. Verify all prerequisites are met
4. Check the troubleshooting section
5. Open an issue on GitHub

## Next Steps

After successful deployment:

1. Add your first products
2. Configure discount rules
3. Test Telegram bot
4. Monitor system performance
5. Set up monitoring alerts
6. Plan for scaling
