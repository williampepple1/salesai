# IAM role for Lambda
resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda.name
}

# Attach VPC execution policy
resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  role       = aws_iam_role.lambda.name
}

# Custom policy for Lambda to access S3 and Secrets Manager
resource "aws_iam_role_policy" "lambda_custom" {
  name = "${var.project_name}-lambda-custom-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.product_images.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.product_images.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.db_credentials.arn,
          aws_secretsmanager_secret.app_secrets.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      }
    ]
  })
}

# Store application secrets
resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${var.project_name}-app-secrets"
  description = "Application secrets for ${var.project_name}"

  recovery_window_in_days = var.environment == "prod" ? 30 : 0
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    openai_api_key        = var.openai_api_key
    telegram_bot_token    = var.telegram_bot_token
    clerk_domain          = var.clerk_domain
    clerk_secret_key      = var.clerk_secret_key
    clerk_publishable_key = var.clerk_publishable_key
  })
}

data "archive_file" "lambda_bootstrap" {
  type        = "zip"
  output_path = "${path.module}/.terraform/lambda-bootstrap.zip"

  source {
    filename = "lambda_handler.py"
    content  = <<-PY
def handler(event, context):
    return {
        "statusCode": 503,
        "headers": {"content-type": "application/json"},
        "body": "{\"detail\":\"Backend package has not been deployed yet\"}"
    }
PY
  }
}

# Lambda function
resource "aws_lambda_function" "api" {
  filename      = data.archive_file.lambda_bootstrap.output_path
  function_name = "${var.project_name}-api"
  role          = aws_iam_role.lambda.arn
  handler       = "lambda_handler.handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 512

  source_code_hash = data.archive_file.lambda_bootstrap.output_base64sha256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  tracing_config {
    mode = var.enable_xray_tracing ? "Active" : "PassThrough"
  }

  environment {
    variables = {
      ENVIRONMENT            = var.environment
      DATABASE_SECRET_ARN    = aws_secretsmanager_secret.db_credentials.arn
      APP_SECRETS_SECRET_ARN = aws_secretsmanager_secret.app_secrets.arn
      AWS_REGION             = var.aws_region
      S3_BUCKET_IMAGES       = aws_s3_bucket.product_images.bucket
      CLERK_DOMAIN           = var.clerk_domain
      CLERK_SECRET_KEY       = var.clerk_secret_key
      CLERK_PUBLISHABLE_KEY  = var.clerk_publishable_key
      OPENAI_API_KEY         = var.openai_api_key
      TELEGRAM_BOT_TOKEN     = var.telegram_bot_token
      TELEGRAM_WEBHOOK_URL   = "${aws_apigatewayv2_api.main.api_endpoint}/api/telegram/webhook"
      CORS_ORIGINS           = jsonencode(local.effective_cors_allowed_origins)
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_iam_role_policy_attachment.lambda_vpc,
    aws_iam_role_policy.lambda_custom
  ]

  lifecycle {
    ignore_changes = [
      filename,
      source_code_hash,
    ]
  }
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = var.cloudwatch_log_retention_days
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
