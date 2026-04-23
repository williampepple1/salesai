# Workflow Modules - Usage Guide

These workflow files are modular components that can be used independently or called by the main deployment workflow.

## Files Overview

### terraform.yml
**Purpose**: Deploy infrastructure (VPC, RDS, Lambda, S3, CloudFront)
**When to use**: Infrastructure changes only
**Run time**: 10-15 minutes

### backend-deploy.yml  
**Purpose**: Build and deploy Lambda function
**When to use**: Backend code changes only
**Run time**: 3-5 minutes
**Requires**: Infrastructure must exist

### frontend-deploy.yml
**Purpose**: Build and deploy React app to S3
**When to use**: Frontend code changes only
**Run time**: 2-3 minutes
**Requires**: S3 bucket and CloudFront must exist

## Using Individual Workflows

If you need to run a specific component independently:

### Method 1: Workflow Call (Recommended)

These workflows support `workflow_call`, so they can be triggered by other workflows:

```yaml
jobs:
  deploy-backend:
    uses: ./.github/workflows/modules/backend-deploy.yml
    secrets: inherit
```

### Method 2: Direct Trigger

1. Temporarily copy the workflow file to the main workflows directory
2. Trigger via GitHub Actions UI
3. Move back to modules after use

### Method 3: Manual Commands

Run the commands directly from your local machine:

```bash
# Infrastructure
cd terraform && terraform apply

# Backend
cd backend && ./build-lambda.sh && aws lambda update-function-code ...

# Frontend  
cd frontend && npm run build && aws s3 sync dist/ s3://bucket/
```

## When to Use Each Workflow

### Use Main deploy.yml When:
- ✅ Deploying for the first time
- ✅ Making changes across multiple components
- ✅ Unsure of dependencies
- ✅ Want automatic ordering
- ✅ Want health checks and verification

### Use Individual Workflows When:
- ✅ Only changing one component (saves time)
- ✅ Debugging specific component
- ✅ Need fine-grained control
- ✅ Testing workflow changes

## Best Practices

1. **Default to main workflow**: Use `deploy.yml` unless you have a specific reason not to
2. **Test locally first**: Always test changes before deploying
3. **Monitor deployments**: Watch the Actions tab during deployment
4. **Check dependencies**: Ensure required components are deployed before dependent ones
5. **Use workflow dispatch**: Leverage the UI for selective deployments

## Deployment Dependencies

```
Infrastructure (Terraform)
    ↓ (creates Lambda, S3, RDS)
Backend (Lambda)
    ↓ (provides API)
Frontend (S3)
```

**Never deploy in the wrong order:**
- ❌ Backend before Infrastructure
- ❌ Frontend before Backend
- ✅ Always: Infrastructure → Backend → Frontend

## Examples

### Example 1: Full Deployment

Use the main workflow:
```bash
git push origin main
```

### Example 2: Backend-Only Update

Use main workflow with selective deployment:
1. GitHub Actions → Complete Deployment
2. Deploy infrastructure: false
3. Deploy backend: true
4. Deploy frontend: false

### Example 3: Frontend Hot Fix

Quick frontend update:
```bash
cd frontend
# Make your changes
git add .
git commit -m "Fix: Button styling"
git push origin main
```

Use selective deployment to only redeploy frontend.

## Troubleshooting Module Workflows

### Workflow Not Found

**Error**: "workflow does not exist"

**Solution**: Ensure the workflow file has:
- `workflow_dispatch:` trigger
- Or `workflow_call:` trigger

### Secrets Not Available

**Error**: "secret not found"

**Solution**: 
- Check secrets are set in repository settings
- Ensure workflow has `secrets: inherit` if called from another workflow

### Dependency Errors

**Error**: "Resource not found"

**Solution**:
- Check previous workflow succeeded
- Verify infrastructure exists
- Run terraform workflow first

## Advanced Usage

### Parallel Deployments (Not Recommended)

While possible, avoid running backend and frontend in parallel as they may have interdependencies.

### Custom Environments

To deploy to different environments:

1. Create separate GitHub environments
2. Add environment-specific secrets
3. Update workflow to use environment parameter
4. Deploy: `workflow_dispatch` with environment input

### Integration with External Tools

These workflows can be:
- Triggered by external webhooks
- Called from other repositories
- Integrated with Slack/Discord notifications

## Monitoring

After running any workflow:

1. **Check Summary**: Green checkmarks for success
2. **View Logs**: Click on jobs for detailed output
3. **Check Artifacts**: Download if workflow produces artifacts
4. **Test Deployment**: Visit URLs to verify functionality

## Need Help?

- Main workflow docs: `../.github/workflows/README.md`
- Full deployment guide: `../../DEPLOYMENT.md`
- Quick start: `../../DEPLOYMENT_GUIDE.md`
