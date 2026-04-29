variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "salesai"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "salesai_admin"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "telegram_bot_token" {
  description = "Telegram bot token"
  type        = string
  sensitive   = true
  default     = ""
}

variable "clerk_domain" {
  description = "Clerk domain (e.g., your-app.clerk.accounts.dev)"
  type        = string
}

variable "clerk_secret_key" {
  description = "Clerk secret key"
  type        = string
  sensitive   = true
}

variable "clerk_publishable_key" {
  description = "Clerk publishable key"
  type        = string
}

variable "frontend_domain" {
  description = "Custom domain for frontend (optional)"
  type        = string
  default     = ""
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for RDS. Production forces this on."
  type        = bool
  default     = false
}

variable "cors_allowed_origins" {
  description = "Allowed browser origins for API Gateway and FastAPI CORS"
  type        = list(string)
  default     = ["http://localhost:5173"]
}

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention for Lambda and API Gateway"
  type        = number
  default     = 30
}

variable "enable_xray_tracing" {
  description = "Enable AWS X-Ray tracing for Lambda"
  type        = bool
  default     = true
}
