# Workflow Modules

This folder contains the individual deployment workflow files that are used by the main deployment workflow.

## Files

- **terraform.yml** - Infrastructure deployment (Terraform)
  - Creates VPC, RDS, Lambda, API Gateway, S3, CloudFront
  - Must run first before other deployments
  - Can be triggered independently for infrastructure-only changes

## Usage

These workflow files are kept here for reference and can be used independently if needed, but the recommended approach is to use the main `deploy.yml` workflow which orchestrates all deployments in the correct order:

1. Infrastructure (Terraform)
2. Backend (Lambda)
3. Frontend (S3 + CloudFront)

## Running Individual Workflows

If you need to run a specific deployment:

1. Copy the workflow file to `.github/workflows/`
2. Trigger it via GitHub Actions UI
3. Move it back to `modules/` folder after use

Or use the main deploy.yml with workflow_dispatch inputs to selectively deploy components.
