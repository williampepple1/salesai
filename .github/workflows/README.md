# GitHub Actions Workflows

This directory contains the CI/CD workflows for the Salesai platform.

## Workflow Architecture

```
┌─────────────────────────────────────────┐
│         deploy.yml (Main)               │
│   Orchestrates Sequential Deployment    │
└────────────────┬────────────────────────┘
                 │
                 ├─── 1. Infrastructure ───┐
                 │    (modules/terraform.yml)
                 │    Creates VPC, RDS,     │
                 │    Lambda, S3, etc.      │
                 │                          ▼
                 │                     [Waits for completion]
                 │                          │
                 ├─── 2. Backend ──────────┤
                 │    (modules/backend-deploy.yml)
                 │    Builds & deploys     │
                 │    Lambda function       │
                 │                          ▼
                 │                     [Waits for completion]
                 │                          │
                 ├─── 3. Frontend ─────────┤
                 │    (modules/frontend-deploy.yml)
                 │    Builds & deploys     │
                 │    to S3 + CloudFront    │
                 │                          ▼
                 │                     [Waits for completion]
                 │                          │
                 └─── 4. Verification ──────┘
                      Health checks & summary
```

## Main Workflow

### deploy.yml (Primary Deployment)

This is the **main deployment workflow** that handles all deployments in the correct sequential order:

```
1. Infrastructure (Terraform) → 2. Backend (Lambda) → 3. Frontend (S3/CloudFront) → 4. Verification
```

**Triggers:**
- Automatic: Push to `main` branch
- Manual: Workflow dispatch with optional component selection

**Features:**
- Sequential deployment with dependency management
- Can deploy all components or select specific ones
- Health checks and verification after deployment
- Detailed deployment summaries
- Rollback safety with skip conditions

**Manual Trigger Options:**
- Deploy Infrastructure (Terraform) - Yes/No
- Deploy Backend (Lambda) - Yes/No  
- Deploy Frontend (S3) - Yes/No

## Workflow Modules

The `modules/` folder contains individual workflow files for reference:

- **terraform.yml** - Infrastructure deployment only

These can be used independently if needed, but it's recommended to use the main `deploy.yml` workflow.

## Deployment Order

The workflows **must** run in this order:

### 1. Infrastructure First (Terraform)
Creates:
- VPC and networking
- RDS PostgreSQL database
- Lambda function configuration
- API Gateway
- S3 buckets
- CloudFront distribution

### 2. Backend Second (Lambda)
- Builds Python Lambda package
- Runs tests
- Updates Lambda function code
- Deploys API endpoints

### 3. Frontend Last (S3 + CloudFront)
- Builds React application
- Uploads to S3
- Invalidates CloudFront cache
- Makes dashboard available

### 4. Verification
- Checks deployment status
- Performs health checks
- Generates deployment report

## Required GitHub Secrets

Add these to your repository settings (Settings → Secrets → Actions):

### AWS Credentials
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Database
- `DB_PASSWORD`

### Services
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`

### Clerk Authentication
- `CLERK_DOMAIN`
- `CLERK_SECRET_KEY`
- `CLERK_PUBLISHABLE_KEY`

### Deployment Targets
- `API_URL` - API Gateway URL
- `S3_FRONTEND_BUCKET` - Frontend S3 bucket name
- `S3_LAMBDA_BUCKET` - Lambda package S3 bucket (optional)
- `CLOUDFRONT_DISTRIBUTION_ID` - CloudFront distribution ID
- `CLOUDFRONT_DOMAIN` - CloudFront domain name

## Usage Examples

### Deploy Everything (Automatic)

```bash
git push origin main
```

All components deploy automatically in sequence.

### Deploy Everything (Manual)

1. Go to Actions tab in GitHub
2. Select "Complete Deployment"
3. Click "Run workflow"
4. Leave all options as "true"
5. Click "Run workflow"

### Deploy Only Backend

1. Go to Actions tab
2. Select "Complete Deployment"  
3. Click "Run workflow"
4. Set:
   - Deploy infrastructure: false
   - Deploy backend: true
   - Deploy frontend: false
5. Click "Run workflow"

### Deploy Only Frontend

1. Go to Actions tab
2. Select "Complete Deployment"
3. Click "Run workflow"
4. Set:
   - Deploy infrastructure: false
   - Deploy backend: false
   - Deploy frontend: true
5. Click "Run workflow"

## Monitoring Deployments

### View Progress

1. Go to Actions tab in GitHub
2. Click on the running workflow
3. See real-time progress of each job

### Check Deployment Summary

After deployment completes, check the summary page for:
- Status of each component
- Deployment links (Frontend URL, API URL)
- Health check results

### View Logs

Click on any job to see detailed logs:
- Infrastructure: Terraform plan and apply output
- Backend: Build logs, test results, Lambda update status
- Frontend: Build output, S3 sync results, CloudFront invalidation

## Troubleshooting

### Infrastructure Fails

**Problem**: Terraform errors
**Solution**: 
- Check AWS credentials
- Verify all secrets are set
- Review Terraform logs for specific errors

### Backend Fails

**Problem**: Lambda deployment errors
**Solution**:
- Check Lambda package size (< 50MB)
- Verify Python dependencies
- Check Lambda function exists

### Frontend Fails

**Problem**: S3 or CloudFront errors
**Solution**:
- Verify S3 bucket exists
- Check CloudFront distribution ID
- Ensure build completes successfully

### Deployment Hangs

**Problem**: Job taking too long
**Solution**:
- Check AWS service status
- Verify network connectivity
- Cancel and retry deployment

## Best Practices

1. **Test Locally First**: Always test changes locally before pushing
2. **Review Plans**: Check Terraform plans before applying
3. **Monitor Deployments**: Watch deployment progress
4. **Keep Secrets Updated**: Rotate credentials regularly
5. **Use Workflow Dispatch**: Test individual components when needed
6. **Check Health**: Always verify deployment with health checks

## Rollback

If a deployment fails:

1. **Infrastructure**: Terraform state is preserved, run again
2. **Backend**: Previous Lambda version remains active
3. **Frontend**: S3 retains previous version, can restore

To rollback manually:
```bash
# Infrastructure
cd terraform && terraform apply -target=specific-resource

# Backend  
aws lambda update-function-code --function-name salesai-api --s3-bucket backup-bucket --s3-key previous-version.zip

# Frontend
aws s3 sync s3://backup-bucket/ s3://frontend-bucket/
```

## Support

- **GitHub Actions Docs**: https://docs.github.com/actions
- **Terraform**: https://terraform.io/docs
- **AWS Lambda**: https://docs.aws.amazon.com/lambda/
- **CloudFront**: https://docs.aws.amazon.com/cloudfront/
