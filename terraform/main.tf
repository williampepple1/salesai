terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }

  backend "s3" {
    bucket = "salesai-terraform-state"
    key    = "state/terraform.tfstate"
    region = "us-east-1"
    # Optional: add dynamodb_table after creating the lock table.
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# Outputs
output "api_gateway_url" {
  description = "API Gateway URL"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "frontend_bucket" {
  description = "Frontend S3 bucket name"
  value       = aws_s3_bucket.frontend.bucket
}

output "frontend_url" {
  description = "Frontend CloudFront URL"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "images_bucket" {
  description = "Product images S3 bucket name"
  value       = aws_s3_bucket.product_images.bucket
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.main.endpoint
}

output "database_secret_arn" {
  description = "Secrets Manager ARN for database credentials"
  value       = aws_secretsmanager_secret.db_credentials.arn
  sensitive   = true
}

output "telegram_webhook_url" {
  description = "Telegram webhook URL"
  value       = "${aws_apigatewayv2_api.main.api_endpoint}/api/telegram/webhook"
}
