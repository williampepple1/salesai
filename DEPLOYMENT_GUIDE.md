# Quick Deployment Guide

This guide shows you how to deploy the AI Sales Helper using the automated deployment workflow.

## Prerequisites Checklist

Before deploying, ensure you have:

- ✅ AWS Account with admin access
- ✅ GitHub repository created
- ✅ Clerk account and API keys ([clerk.com](https://clerk.com))
- ✅ OpenAI API key
- ✅ Telegram bot token (from @BotFather)

## Step 1: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJalrXUtnFEMI/K7MDENG/...` |
| `DB_PASSWORD` | Database password | `SecurePassword123!` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `1234567890:ABCdef...` |
| `CLERK_DOMAIN` | Clerk domain | `your-app.clerk.accounts.dev` |
| `CLERK_SECRET_KEY` | Clerk secret key | `sk_test_...` |
| `CLERK_PUBLISHABLE_KEY` | Clerk publishable key | `pk_test_...` |
| `API_URL` | API Gateway URL | Set after first deploy |
| `S3_FRONTEND_BUCKET` | Frontend bucket name | `salesai-frontend-123456789` |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront ID | `E1234567890ABC` |
| `CLOUDFRONT_DOMAIN` | CloudFront domain | `d123456.cloudfront.net` |

## Step 2: Update Terraform Variables

1. Copy `terraform/terraform.tfvars.example` to `terraform/terraform.tfvars`
2. Fill in your values:

```hcl
project_name = "salesai"
environment  = "prod"
aws_region   = "us-east-1"

db_username = "salesai_admin"
db_password = "YOUR_SECURE_PASSWORD"  # Match GitHub secret

openai_api_key         = "sk-your-key"
telegram_bot_token     = "your-token"
clerk_domain           = "your-app.clerk.accounts.dev"
clerk_secret_key       = "sk_test_your-key"
clerk_publishable_key  = "pk_test_your-key"
```

## Step 3: Initial Deployment

### Option A: Push to Main (Automatic)

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

GitHub Actions will automatically deploy everything in sequence.

### Option B: Manual Trigger (GitHub UI)

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Complete Deployment** workflow
4. Click **Run workflow** button
5. Leave all options as "true"
6. Click **Run workflow**

## Step 4: Monitor Deployment

Watch the deployment progress:

```
🏗️ Step 1: Infrastructure (5-15 minutes)
  - Creating VPC and networking
  - Launching RDS database
  - Setting up Lambda and API Gateway
  - Creating S3 buckets
  - Configuring CloudFront

⏳ Waiting for infrastructure...

🐍 Step 2: Backend (2-5 minutes)
  - Installing Python dependencies
  - Running tests
  - Building Lambda package
  - Deploying to Lambda

⏳ Waiting for backend...

⚛️ Step 3: Frontend (2-3 minutes)
  - Installing Node dependencies
  - Building React app
  - Uploading to S3
  - Invalidating CloudFront cache

✅ Step 4: Verification
  - Health checks
  - Deployment summary
```

**Total time: ~10-25 minutes** (first deployment takes longer)

## Step 5: Post-Deployment Setup

After deployment completes:

### Get Your URLs

From the GitHub Actions summary or Terraform output:

- **Frontend URL**: `https://your-cloudfront-domain.cloudfront.net`
- **API URL**: `https://your-api-id.execute-api.us-east-1.amazonaws.com`

### Update GitHub Secrets

Add the URLs you received:

- `API_URL`: Your API Gateway URL
- `CLOUDFRONT_DOMAIN`: Your CloudFront domain

### Configure Telegram Bot

1. Open your dashboard at the Frontend URL
2. Sign up / Sign in with Clerk
3. Go to Settings
4. Enter your Telegram bot token
5. Click Save

Your bot will automatically be configured with the webhook!

## Step 6: Test Everything

### Test Dashboard

1. Visit your frontend URL
2. Sign in with Clerk
3. Add a test product
4. Create a discount rule

### Test Telegram Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Try browsing products
5. Test placing an order

## Deployment Options

### Deploy Everything

```bash
git push origin main
```

Or via GitHub UI: Run workflow with all options enabled

### Deploy Only Backend

Via GitHub UI:
1. Actions → Complete Deployment → Run workflow
2. Set:
   - Deploy infrastructure: ❌ false
   - Deploy backend: ✅ true
   - Deploy frontend: ❌ false

### Deploy Only Frontend

Via GitHub UI:
1. Actions → Complete Deployment → Run workflow
2. Set:
   - Deploy infrastructure: ❌ false
   - Deploy backend: ❌ false
   - Deploy frontend: ✅ true

## Updating Your Application

### Update Backend Code

```bash
# Make changes to backend/
git add backend/
git commit -m "Update backend"
git push origin main
```

Only backend will redeploy (unless infrastructure changed)

### Update Frontend Code

```bash
# Make changes to frontend/
git add frontend/
git commit -m "Update frontend"
git push origin main
```

Only frontend will redeploy

### Update Infrastructure

```bash
# Make changes to terraform/
git add terraform/
git commit -m "Update infrastructure"
git push origin main
```

All components will redeploy in sequence

## Troubleshooting

### Deployment Failed: Infrastructure

**Problem**: Terraform errors

**Solutions**:
- Check AWS credentials are correct
- Verify all secrets are set in GitHub
- Check Terraform logs in Actions
- Ensure AWS region has capacity

### Deployment Failed: Backend

**Problem**: Lambda deployment failed

**Solutions**:
- Verify infrastructure deployed successfully
- Check Python dependencies
- Ensure Lambda function exists in AWS console
- Check CloudWatch logs

### Deployment Failed: Frontend

**Problem**: S3 or CloudFront error

**Solutions**:
- Verify S3 bucket name is correct
- Check CloudFront distribution ID
- Ensure build completed successfully
- Check CORS settings

### Application Not Working

**Problem**: 500 errors or app not loading

**Solutions**:
- Check CloudWatch logs for Lambda
- Verify database connection
- Check API Gateway logs
- Verify Clerk configuration
- Test API health endpoint: `https://your-api-url/health`

## Rollback

If something goes wrong:

### Via GitHub

1. Go to Actions
2. Find last successful deployment
3. Re-run that workflow

### Via AWS Console

1. **Backend**: Lambda → Versions → Publish new version from previous
2. **Frontend**: S3 → Previous version → Restore
3. **Infrastructure**: Terraform state is preserved

## Cost Monitoring

After deployment, monitor costs:

- **RDS**: ~$15/month (db.t3.micro)
- **Lambda**: ~$5/month (free tier + usage)
- **S3**: ~$1/month
- **CloudFront**: ~$1/month
- **NAT Gateway**: ~$32/month
- **Total**: ~$55-60/month

Consider:
- Use db.t4g.micro for cost savings
- Enable RDS auto-scaling
- Use CloudFront caching effectively

## Support

- **Workflow Issues**: Check [.github/workflows/README.md](.github/workflows/README.md)
- **Deployment Errors**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Clerk Setup**: See [CLERK_SETUP.md](CLERK_SETUP.md)
- **General Issues**: Check [README.md](README.md)

## Next Steps

After successful deployment:

1. ✅ Add your products
2. ✅ Configure discount rules
3. ✅ Test Telegram bot thoroughly
4. ✅ Monitor CloudWatch logs
5. ✅ Set up CloudWatch alarms
6. ✅ Configure custom domain (optional)
7. ✅ Enable CloudFront custom SSL (optional)

Congratulations! Your AI Sales Helper is now live! 🎉
