# Salesai

A complete AI-powered sales assistant platform that enables sellers to manage products through a dashboard and automatically handle customer conversations via Telegram when offline. The AI agent can show products, calculate discounts, and process orders autonomously.

## 🎯 Quick Links

- **⚡ Deploy in 30 minutes**: [QUICKSTART.md](QUICKSTART.md)
- **📊 Project Overview**: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- **🚀 Automated Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **🔐 Clerk Auth Setup**: [CLERK_SETUP.md](CLERK_SETUP.md)
- **🤖 AI Agent Guide**: [AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md)

## Features

- **Clerk Authentication**: Production-ready auth with email, social logins, 2FA, and user management
- **React Dashboard**: Product management, discount configuration, order tracking, and Telegram bot integration
- **AI Sales Agent**: OpenAI GPT-4 powered conversational agent for customer interactions (with strict product-only guardrails)
- **Telegram Bot**: Seamless integration with Telegram for customer communication
- **Smart Discounts**: Flexible discount rules (percentage, fixed amount, buy X get Y free)
- **Image Management**: Direct S3 uploads for product images
- **Order Processing**: Complete order management with status tracking
- **AWS Infrastructure**: Serverless deployment with Lambda, RDS, S3, and CloudFront
- **CI/CD Pipeline**: Automated deployment with GitHub Actions

## Architecture

```
┌─────────────┐
│  Customer   │
│  (Telegram) │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│    API Gateway + Lambda             │
│  ┌────────────────────────────┐    │
│  │   Telegram Bot Handler     │    │
│  └────────────┬───────────────┘    │
│               ▼                     │
│  ┌────────────────────────────┐    │
│  │   AI Agent (OpenAI GPT-4)  │    │
│  └────────────┬───────────────┘    │
│               ▼                     │
│  ┌────────────────────────────┐    │
│  │    Discount Engine         │    │
│  └────────────────────────────┘    │
└──────────────┬──────────────────────┘
               │
               ▼
      ┌────────────────┐
      │  PostgreSQL    │
      │     (RDS)      │
      └────────────────┘

┌─────────────┐         ┌────────────────┐
│   Seller    │────────▶│  React Dashboard│
│             │         │  (S3+CloudFront)│
└─────────────┘         └────────────────┘
```

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast builds
- **TailwindCSS** for styling
- **React Query** for data fetching
- **React Router** for navigation
- **Clerk** for authentication

### Backend
- **Python 3.11** with FastAPI
- **SQLAlchemy** for ORM
- **PostgreSQL** for database
- **Clerk** for authentication & user management
- **OpenAI API** for AI agent
- **Telegram Bot API** for messaging
- **Mangum** for Lambda integration

### Infrastructure
- **AWS Lambda** for serverless compute
- **API Gateway** for HTTP routing
- **RDS PostgreSQL** for database
- **S3** for static hosting and images
- **CloudFront** for CDN
- **Secrets Manager** for credentials
- **VPC** for network isolation
- **Terraform** for IaC
- **GitHub Actions** for CI/CD

## Prerequisites

- AWS Account with administrative access (or appropriate IAM permissions)
- Node.js 18+
- Python 3.11+
- Terraform 1.6+
- Git
- AWS CLI installed and configured
- **Clerk account** (free tier available at [clerk.com](https://clerk.com))
- OpenAI API key (from [platform.openai.com](https://platform.openai.com))
- Telegram bot token (from @BotFather)

## Setup Instructions

### 1. AWS Account Setup and IAM Configuration

#### 1.1 Create AWS Account (if you don't have one)

1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Follow the registration process:
   - Enter email address and account name
   - Provide contact information
   - Enter payment information (required, but free tier available)
   - Verify your identity via phone
   - Select "Basic Support - Free" plan
4. Sign in to AWS Console after account creation

#### 1.2 Create IAM User for Deployment

**⚠️ IMPORTANT: Never use root account credentials for deployment. Always create an IAM user.**

1. **Sign in to AWS Console** as root user or administrator
2. **Navigate to IAM Service**:
   - Search for "IAM" in the AWS Console search bar
   - Click on "IAM" (Identity and Access Management)

3. **Create a new IAM user**:
   - Click "Users" in the left sidebar
   - Click "Add users" button
   - Enter username: `aiengineer` (or your preferred name)
   - Select "Provide user access to the AWS Management Console" (optional, for console access)
   - Select "I want to create an IAM user"
   - Choose "Custom password" and enter a strong password
   - Uncheck "User must create a new password at next sign-in" (optional)
   - Click "Next"

4. **Attach Policies to User**:
   
   **Option A: Use AdministratorAccess (Easiest, less secure)**
   - Click "Attach policies directly"
   - Search for "AdministratorAccess"
   - Check the box next to "AdministratorAccess"
   - Click "Next"
   - ⚠️ Warning: This gives full access to your AWS account. Only use for development/testing.

   **Option B: Create Custom Policy (Recommended, more secure)**
   - Click "Create policy" (opens in new tab)
   - Click "JSON" tab
   - Paste the following minimal policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "rds:*",
                "s3:*",
                "lambda:*",
                "apigateway:*",
                "cloudfront:*",
                "iam:*",
                "secretsmanager:*",
                "logs:*",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

   - Click "Next: Tags"
   - (Optional) Add tags like `Project: salesai`
   - Click "Next: Review"
   - Name the policy: `SalesAI-Deployment-Policy`
   - Add description: "Policy for deploying SalesAI infrastructure"
   - Click "Create policy"
   - Return to the previous tab (Create user)
   - Click the refresh button next to "Create policy"
   - Search for "SalesAI-Deployment-Policy"
   - Check the box next to your newly created policy
   - Click "Next"

5. **Review and Create**:
   - Review the user details
   - Click "Create user"
   - ✅ User created successfully!

#### 1.3 Create Access Keys for Programmatic Access

1. **Navigate to your new user**:
   - Click on the username (`aiengineer`)
   
2. **Create Access Key**:
   - Click the "Security credentials" tab
   - Scroll down to "Access keys" section
   - Click "Create access key"
   
3. **Select Use Case**:
   - Select "Command Line Interface (CLI)"
   - Check the confirmation box "I understand the above recommendation..."
   - Click "Next"
   
4. **Set Description Tag** (optional):
   - Enter description: "SalesAI deployment access key"
   - Click "Create access key"
   
5. **Save Your Credentials** ⚠️ CRITICAL:
   - **Access Key ID**: `AKIAIOSFODNN7EXAMPLE` (example)
   - **Secret Access Key**: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` (example)
   - Click "Download .csv file" to save credentials
   - **⚠️ IMPORTANT: This is the ONLY time you can view the secret key!**
   - Store this file in a secure location (not in your git repository)
   - Click "Done"

#### 1.4 Configure AWS CLI with Your Credentials

1. **Install AWS CLI** (if not already installed):
   
   **Windows:**
   ```powershell
   msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
   ```
   
   **macOS:**
   ```bash
   brew install awscli
   ```
   
   **Linux:**
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **Verify Installation**:
   ```bash
   aws --version
   # Should output: aws-cli/2.x.x ...
   ```

3. **Configure AWS Credentials**:
   ```bash
   aws configure
   ```
   
   Enter the following when prompted:
   ```
   AWS Access Key ID [None]: PASTE_YOUR_ACCESS_KEY_ID
   AWS Secret Access Key [None]: PASTE_YOUR_SECRET_ACCESS_KEY
   Default region name [None]: us-east-1
   Default output format [None]: json
   ```

4. **Verify Configuration**:
   ```bash
   aws sts get-caller-identity
   ```
   
   You should see output like:
   ```json
   {
       "UserId": "AIDAI23HXI2EXAMPLE",
       "Account": "123456789012",
       "Arn": "arn:aws:iam::123456789012:user/aiengineer"
   }
   ```

5. **Test Permissions**:
   ```bash
   aws s3 ls
   # Should list S3 buckets or show empty (no error)
   
   aws ec2 describe-regions
   # Should list AWS regions
   ```

#### 1.5 Additional IAM Roles (Created Automatically by Terraform)

The following roles will be created automatically during Terraform deployment:
- **Lambda Execution Role**: Allows Lambda functions to write logs and access RDS
- **API Gateway Role**: Allows API Gateway to invoke Lambda functions
- **CloudFront OAI**: Allows CloudFront to read from S3 bucket

You don't need to create these manually - Terraform handles this.

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/salesai.git
cd salesai
```

### 3. Install Required Tools

#### 3.1 Install Node.js (if not installed)

**Windows:**
- Download from [nodejs.org](https://nodejs.org)
- Run the installer (choose LTS version 18+)
- Verify installation:
  ```powershell
  node --version
  npm --version
  ```

**macOS:**
```bash
brew install node@18
node --version
npm --version
```

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
npm --version
```

#### 3.2 Install Python 3.11 (if not installed)

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Run installer and check "Add Python to PATH"
- Verify:
  ```powershell
  python --version
  pip --version
  ```

**macOS:**
```bash
brew install python@3.11
python3.11 --version
pip3 --version
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3.11 --version
pip3 --version
```

#### 3.3 Install Terraform

**Windows:**
- Download from [terraform.io](https://www.terraform.io/downloads)
- Extract to a folder (e.g., `C:\terraform`)
- Add to PATH environment variable
- Verify:
  ```powershell
  terraform --version
  ```

**macOS:**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
terraform --version
```

**Linux:**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
terraform --version
```

### 4. Set Up Terraform Backend (Optional but Recommended)

#### 4.1 Create S3 Bucket for Terraform State

This bucket will store your Terraform state file securely.

1. **Create the bucket**:
   ```bash
   aws s3 mb s3://salesai-terraform-state-YOUR-UNIQUE-ID --region us-east-1
   ```
   
   Replace `YOUR-UNIQUE-ID` with something unique (e.g., your AWS account ID or random string)

2. **Enable versioning** (recommended for state file recovery):
   ```bash
   aws s3api put-bucket-versioning \
     --bucket salesai-terraform-state-YOUR-UNIQUE-ID \
     --versioning-configuration Status=Enabled
   ```

3. **Enable encryption**:
   ```bash
   aws s3api put-bucket-encryption \
     --bucket salesai-terraform-state-YOUR-UNIQUE-ID \
     --server-side-encryption-configuration '{
       "Rules": [{
         "ApplyServerSideEncryptionByDefault": {
           "SSEAlgorithm": "AES256"
         }
       }]
     }'
   ```

4. **Block public access** (security best practice):
   ```bash
   aws s3api put-public-access-block \
     --bucket salesai-terraform-state-YOUR-UNIQUE-ID \
     --public-access-block-configuration \
       "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
   ```

#### 4.2 Update Terraform Configuration

Edit `terraform/main.tf` and update the backend configuration:

```hcl
terraform {
  backend "s3" {
    bucket         = "salesai-terraform-state-YOUR-UNIQUE-ID"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
  }
}
```

### 5. Set Up OpenAI API

#### 5.1 Create OpenAI Account

1. **Go to** [platform.openai.com](https://platform.openai.com)
2. **Click "Sign up"**
3. Create account using:
   - Email address, or
   - Google account, or
   - Microsoft account
4. **Verify your email** if using email signup
5. **Complete profile setup**

#### 5.2 Add Payment Method

⚠️ OpenAI requires a payment method to use the API (even for small usage)

1. **Navigate to** [platform.openai.com/account/billing/overview](https://platform.openai.com/account/billing/overview)
2. **Click "Add payment details"**
3. **Enter credit card information**
4. **Set usage limits** (recommended):
   - Click "Usage limits"
   - Set "Hard limit": $50 (or your preferred amount)
   - Set "Soft limit": $25 (you'll get notified)
   - Click "Save"

#### 5.3 Create API Key

1. **Navigate to** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. **Click "+ Create new secret key"**
3. **Name your key**: `salesai-production` (or your preferred name)
4. **Set permissions**:
   - Select "All" (or "Restricted" if you want limited access)
5. **Click "Create secret key"**
6. **⚠️ COPY THE KEY IMMEDIATELY**:
   - Format: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **This is the only time you'll see it!**
   - Store it securely - you'll add it to `.env` later
7. **Click "Done"**

#### 5.4 Verify API Access

Test your API key:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY"
```

If successful, you'll see a list of available models including `gpt-4`.

### 6. Set Up Telegram Bot

#### 6.1 Create Telegram Account (if needed)

1. Download Telegram app: [telegram.org](https://telegram.org)
2. Install and create account using your phone number
3. Verify with SMS code

#### 6.2 Create Your Bot with BotFather

1. **Open Telegram** on your phone or desktop
2. **Search for** `@BotFather` (official bot with blue checkmark)
3. **Start conversation**: Click "Start" or send `/start`
4. **Create new bot**:
   - Send: `/newbot`
   - BotFather will ask for a name

5. **Enter bot name**:
   - Message: `My Sales AI Bot` (or any name you like)
   - This is the display name users will see

6. **Enter bot username**:
   - Must end with `bot`
   - Must be unique on Telegram
   - Example: `mysalesai_bot` or `your_company_sales_bot`
   - Must be one word (no spaces)

7. **Save your bot token** ⚠️ CRITICAL:
   - BotFather will respond with:
   ```
   Done! Congratulations on your new bot...
   
   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-EXAMPLE
   
   Keep your token secure...
   ```
   - **Copy this token** - you'll need it for `.env` file
   - Format: `<bot_id>:<secret_token>`

8. **Configure bot settings** (optional but recommended):
   
   **Set description**:
   ```
   /setdescription
   ```
   Then select your bot and enter:
   ```
   I'm your AI sales assistant! I can show you products, calculate discounts, and help you place orders.
   ```
   
   **Set about text**:
   ```
   /setabouttext
   ```
   Then select your bot and enter:
   ```
   AI-powered sales assistant for [Your Store Name]
   ```
   
   **Set bot picture**:
   ```
   /setuserpic
   ```
   Then select your bot and upload an image (optional)
   
   **Set commands** (helps users see available commands):
   ```
   /setcommands
   ```
   Then select your bot and paste:
   ```
   start - Start conversation with the bot
   browse - Browse all products
   cart - View your shopping cart
   help - Get help
   ```

#### 6.3 Test Your Bot

1. **Find your bot** in Telegram search (search for the username you created)
2. **Click "Start"**
3. You should see: "Bot is not yet configured" or similar message
4. This is normal - we'll configure it later after deployment

#### 6.4 Important Security Note

⚠️ **Never share your bot token publicly**:
- Don't commit it to git
- Don't post it in forums/chat
- If exposed, use `/revoke` with BotFather to get a new token

### 7. Set Up Clerk Authentication

#### 7.1 Create Clerk Account

1. **Go to** [clerk.com](https://clerk.com)
2. **Click "Sign up"** (top right)
3. **Create account** using:
   - Email and password, or
   - Sign up with Google, or
   - Sign up with GitHub
4. **Verify your email** if using email signup

#### 7.2 Create Your Application

1. **After signing in**, you'll see "Create application" screen
2. **Enter application name**: `SalesAI Dashboard` (or your preferred name)
3. **Choose sign-in methods** (check what you want to enable):
   - ✅ Email address (recommended - always enable)
   - ✅ Google (optional - easy for users)
   - ✅ GitHub (optional)
   - ✅ Microsoft (optional)
   - ✅ Phone number (optional - for SMS verification)
   - You can change these later
4. **Select environment**: Leave as "Development" for now
5. **Click "Create application"**

#### 7.3 Get Your API Keys

After creating the application:

1. **You'll be redirected** to the application dashboard
2. **Navigate to "API Keys"** (left sidebar)
3. **You'll see three keys**:

   **Frontend API Key** (publishable key):
   - Starts with `pk_test_` (test) or `pk_live_` (production)
   - Example: `pk_test_Y2xlcmsuaGVhbHRoLmt3YWwuNTQkABCDEFGH`
   - ✅ Safe to expose in frontend code
   - Copy this to clipboard
   
   **Secret Key** (backend key):
   - Starts with `sk_test_` (test) or `sk_live_` (production)
   - Example: `sk_test_ABCdefGHIjklMNOpqrsTUVwxyz123456789`
   - ⚠️ MUST be kept secret - never expose in frontend
   - Copy this to clipboard
   
   **Clerk Domain**:
   - Format: `your-app-name.clerk.accounts.dev` (development)
   - Or custom domain like `auth.yourdomain.com` (production)
   - Example: `health-kwal-54.clerk.accounts.dev`
   - Copy this to clipboard

4. **Save all three values** - you'll need them for `.env` file

#### 7.4 Configure Application Settings

1. **Navigate to "Settings" → "General"** (left sidebar)
2. **Session settings** (optional but recommended):
   - Click "Sessions" in left sidebar
   - Set "Session lifetime": 7 days (default)
   - Enable "Multi-session handling" if you want users to login from multiple devices
3. **Save changes**

#### 7.5 Configure Allowed Origins (CORS)

⚠️ Important: This allows your deployed frontend to communicate with Clerk

1. **Navigate to "Settings" → "Domains"**
2. **Development** (for local testing):
   - `http://localhost:5173` (React dev server)
   - `http://localhost:8000` (FastAPI dev server)
3. **Production** (add after deployment):
   - Your CloudFront URL (e.g., `https://d1234567890.cloudfront.net`)
   - Your custom domain if you have one

Note: You'll update this after deploying to add your production URLs.

#### 7.6 Enable Email Verification (Recommended)

1. **Navigate to "User & Authentication" → "Email, Phone, Username"**
2. **Email address settings**:
   - Toggle "Verification" to ON
   - This sends verification email to new users
3. **Customize email template** (optional):
   - Click "Emails" in left sidebar
   - Customize verification email template
   - Add your branding

#### 7.7 Test Clerk Setup

You can test your Clerk setup later after deploying the frontend. For now, just ensure you have:
- ✅ Clerk account created
- ✅ Application created
- ✅ Frontend API Key (publishable key) copied
- ✅ Secret Key copied
- ✅ Clerk Domain copied

📖 **For more detailed Clerk configuration, see [CLERK_SETUP.md](CLERK_SETUP.md)**

### 8. Configure Environment Variables

#### 8.1 Understanding Environment Variables

This project uses environment variables to store sensitive configuration. These variables are:
- **Never committed to git** (`.env` is in `.gitignore`)
- **Different for each environment** (development vs production)
- **Stored securely in AWS Secrets Manager** for production

#### 8.2 Create .env File

A `.env` file has been created in the root folder. Now let's fill it in:

1. **Open** `.env` file in your editor
2. **Fill in each value** using the credentials you created above

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID_FROM_IAM_USER
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY_FROM_IAM_USER

# Database Configuration (create a strong password)
DB_USERNAME=salesai_admin
DB_PASSWORD=CREATE_A_STRONG_PASSWORD_HERE
# Password requirements:
# - At least 12 characters
# - Include uppercase, lowercase, numbers, special characters
# - No spaces
# - Example: MyS3cur3P@ssw0rd!2024

# Clerk Authentication (from step 7.3)
CLERK_DOMAIN=your-app-name.clerk.accounts.dev
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key_here
CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key_here

# OpenAI Configuration (from step 5.3)
OPENAI_API_KEY=sk-proj-your_openai_api_key_here

# Telegram Configuration (from step 6.2)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# S3 Configuration (leave these as-is, they'll be created during deployment)
S3_BUCKET_IMAGES=salesai-product-images-${random_id}
S3_FRONTEND_BUCKET=salesai-frontend-${random_id}

# API Configuration (will be set after Terraform deployment)
API_URL=https://your-api-gateway-url.amazonaws.com/api
TELEGRAM_WEBHOOK_URL=https://your-api-gateway-url.amazonaws.com/api/telegram/webhook

# Frontend Configuration (will be set after deployment)
CLOUDFRONT_DISTRIBUTION_ID=ABCDEFGH12345
CLOUDFRONT_DOMAIN=d1234567890.cloudfront.net
```

3. **Save the file**

#### 8.3 Verify Environment Variables

Double-check that you've filled in these critical values:
- [ ] AWS_ACCESS_KEY_ID (from IAM user)
- [ ] AWS_SECRET_ACCESS_KEY (from IAM user)
- [ ] DB_PASSWORD (strong password you created)
- [ ] CLERK_DOMAIN (from Clerk dashboard)
- [ ] CLERK_SECRET_KEY (from Clerk dashboard)
- [ ] CLERK_PUBLISHABLE_KEY (from Clerk dashboard)
- [ ] OPENAI_API_KEY (from OpenAI platform)
- [ ] TELEGRAM_BOT_TOKEN (from BotFather)

**📖 For detailed instructions on each variable, see [.env.setup.md](.env.setup.md)**

### 9. Configure Terraform Variables

#### 9.1 Navigate to Terraform Directory

```bash
cd terraform
```

#### 9.2 Create terraform.tfvars File

This file contains your actual values (never commit this to git).

1. **Copy the example file**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Edit terraform.tfvars** with your actual values:

```hcl
# Project Configuration
project_name = "salesai"
environment  = "dev"  # or "staging", "production"
aws_region   = "us-east-1"  # Choose your preferred region

# Database Configuration (use same password from .env)
db_username = "salesai_admin"
db_password = "YOUR_SECURE_PASSWORD_FROM_ENV_FILE"

# OpenAI Configuration
openai_api_key = "sk-proj-your_openai_api_key_here"

# Telegram Configuration
telegram_bot_token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# Clerk Authentication
clerk_domain           = "your-app-name.clerk.accounts.dev"
clerk_secret_key       = "sk_test_your_clerk_secret_key_here"
clerk_publishable_key  = "pk_test_your_clerk_publishable_key_here"

# Optional: VPC CIDR (change if you have conflicts)
vpc_cidr = "10.0.0.0/16"

# Optional: Database instance type (increase for production)
db_instance_class = "db.t3.micro"  # Cheapest option ($15/month)
# For production, consider: "db.t3.small" or "db.t3.medium"

# Optional: Lambda memory (affects performance and cost)
lambda_memory_size = 512  # MB
# Increase to 1024 or 2048 for better performance
```

3. **Save the file**

#### 9.3 Review Terraform Configuration Files

Before deploying, let's understand what Terraform will create:

**VPC & Networking** (`vpc.tf`):
- VPC with CIDR block 10.0.0.0/16
- 2 public subnets (for NAT Gateway)
- 2 private subnets (for Lambda and RDS)
- Internet Gateway
- NAT Gateway (for Lambda to access internet)
- Route tables and associations

**RDS Database** (`rds.tf`):
- PostgreSQL 14 instance
- Located in private subnet (not accessible from internet)
- Security group allowing only Lambda access
- Automated backups enabled
- Multi-AZ disabled (single instance for cost)

**Lambda Functions** (`lambda.tf`):
- API Lambda function (FastAPI application)
- VPC configuration (can access RDS)
- Environment variables from Secrets Manager
- IAM role with necessary permissions

**API Gateway** (`api_gateway.tf`):
- HTTP API (cheaper than REST API)
- Routes for all endpoints
- CORS configuration
- Lambda integration

**S3 Buckets** (`s3.tf`):
- Frontend hosting bucket (website)
- Product images bucket
- Bucket policies for CloudFront access

**CloudFront** (`cloudfront.tf`):
- CDN for frontend
- HTTPS enabled
- Origin Access Identity for S3

**Secrets Manager** (`secrets.tf`):
- Stores all sensitive credentials
- Used by Lambda functions

**IAM Roles & Policies** (`iam.tf`):
- Lambda execution role
- Policies for S3, RDS, Secrets Manager access

### 10. Deploy Infrastructure with Terraform

#### 10.1 Initialize Terraform

This downloads required providers (AWS, Random, etc.):

```bash
terraform init
```

Expected output:
```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.x.x...
- Installed hashicorp/aws v5.x.x

Terraform has been successfully initialized!
```

#### 10.2 Validate Configuration

Check for syntax errors:

```bash
terraform validate
```

Expected output:
```
Success! The configuration is valid.
```

#### 10.3 Preview Infrastructure Changes

See what Terraform will create:

```bash
terraform plan
```

This shows:
- **Resources to add**: ~50-60 resources (VPC, subnets, Lambda, RDS, etc.)
- **Resources to change**: 0 (first time)
- **Resources to destroy**: 0 (first time)

Review the plan carefully. You should see:
- ✅ VPC and networking resources
- ✅ RDS PostgreSQL instance
- ✅ Lambda function
- ✅ API Gateway
- ✅ S3 buckets
- ✅ CloudFront distribution
- ✅ IAM roles and policies
- ✅ Security groups
- ✅ Secrets Manager secrets

#### 10.4 Deploy Infrastructure

Apply the Terraform configuration:

```bash
terraform apply
```

1. **Review the plan** one more time
2. **Type `yes`** when prompted
3. **Wait 10-15 minutes** for deployment to complete

What's happening during deployment:
- **Minutes 0-2**: Creating VPC, subnets, security groups (fast)
- **Minutes 2-5**: Creating NAT Gateway, Internet Gateway (medium)
- **Minutes 5-12**: Creating RDS database (slow - this takes longest)
- **Minutes 12-13**: Creating Lambda function
- **Minutes 13-14**: Creating API Gateway
- **Minutes 14-15**: Creating CloudFront distribution (can take longer)

Expected output at the end:
```
Apply complete! Resources: 57 added, 0 changed, 0 destroyed.

Outputs:

api_gateway_url = "https://abc123xyz.execute-api.us-east-1.amazonaws.com"
frontend_url = "https://d1234567890.cloudfront.net"
telegram_webhook_url = "https://abc123xyz.execute-api.us-east-1.amazonaws.com/telegram/webhook"
rds_endpoint = "salesai-dev-db.abc123.us-east-1.rds.amazonaws.com:5432"
s3_frontend_bucket = "salesai-frontend-abc123"
s3_images_bucket = "salesai-product-images-abc123"
cloudfront_distribution_id = "E1234ABCD5678"
```

#### 10.5 Save Terraform Outputs

⚠️ **IMPORTANT**: Save these outputs - you'll need them!

1. **Copy the outputs** to a safe place (notepad, password manager, etc.)

2. **Update your .env file** with the actual values:

```bash
# Update these in your .env file
API_URL=https://abc123xyz.execute-api.us-east-1.amazonaws.com/api
TELEGRAM_WEBHOOK_URL=https://abc123xyz.execute-api.us-east-1.amazonaws.com/api/telegram/webhook
CLOUDFRONT_DISTRIBUTION_ID=E1234ABCD5678
CLOUDFRONT_DOMAIN=d1234567890.cloudfront.net
S3_FRONTEND_BUCKET=salesai-frontend-abc123
```

3. **You can always retrieve outputs later**:
   ```bash
   terraform output
   # Shows all outputs
   
   terraform output api_gateway_url
   # Shows specific output
   ```

#### 10.6 Verify Infrastructure Deployment

Test that everything was created successfully:

1. **Check VPC**:
   ```bash
   aws ec2 describe-vpcs --filters "Name=tag:Name,Values=salesai-dev-vpc"
   ```

2. **Check RDS**:
   ```bash
   aws rds describe-db-instances --db-instance-identifier salesai-dev-db
   ```

3. **Check Lambda**:
   ```bash
   aws lambda get-function --function-name salesai-dev-api
   ```

4. **Check S3 buckets**:
   ```bash
   aws s3 ls | grep salesai
   ```

5. **Check API Gateway**:
   ```bash
   aws apigatewayv2 get-apis | grep salesai
   ```

All commands should return data (not errors).

#### 10.7 Troubleshooting Terraform Deployment

**Error: "Access Denied" or "UnauthorizedOperation"**
- ✅ Solution: Your IAM user doesn't have sufficient permissions
- Check IAM policies from step 1.2
- Ensure you have permissions for EC2, RDS, Lambda, S3, etc.

**Error: "InvalidParameterValue: DB Password"**
- ✅ Solution: Password doesn't meet requirements
- Must be 8-41 characters
- No special characters: `@`, `/`, `"`, or space
- Use: letters, numbers, and `!#$%&'()*+,-./:;<=>?[\]^_{|}~`

**Error: "VPC Limit Exceeded"**
- ✅ Solution: You've reached AWS VPC limit (default: 5 per region)
- Either delete unused VPCs or request limit increase
- AWS Console → VPC → Delete unused VPCs

**Error: "RDS DB Instance ... already exists"**
- ✅ Solution: Previous deployment wasn't fully cleaned up
- Delete the RDS instance manually or use different `project_name`

**Error: "CloudFront distribution creation timeout"**
- ✅ Solution: CloudFront takes 15-30 minutes to deploy
- This is normal - just wait longer
- Or run `terraform apply` again - it will continue where it left off

**Terraform state locked**
- ✅ Solution: Previous `terraform apply` was interrupted
- Run: `terraform force-unlock <lock-id>`
- Lock ID is shown in the error message

### 11. Set Up GitHub Secrets for CI/CD

GitHub Actions needs access to your AWS account and other credentials to deploy automatically. Let's add them securely.

#### 11.1 Navigate to GitHub Repository Settings

1. **Go to your GitHub repository** (fork or your own repo)
2. **Click "Settings"** tab (top navigation)
3. **Click "Secrets and variables"** in left sidebar
4. **Click "Actions"**
5. **Click "New repository secret"** button

#### 11.2 Add Each Secret

Add the following secrets one by one. For each:
1. Click "New repository secret"
2. Enter "Name" (exact name as shown below)
3. Enter "Value" (paste your actual value)
4. Click "Add secret"

**AWS Credentials** (from step 1.3):

| Secret Name | Value | Where to Find |
|------------|-------|---------------|
| `AWS_ACCESS_KEY_ID` | Your IAM access key | From IAM user creation (step 1.3) |
| `AWS_SECRET_ACCESS_KEY` | Your IAM secret key | From IAM user creation (step 1.3) |
| `AWS_REGION` | `us-east-1` | Your chosen AWS region |

**Database** (from step 8.2):

| Secret Name | Value | Where to Find |
|------------|-------|---------------|
| `DB_PASSWORD` | Your database password | The password you created in .env file |

**Clerk Authentication** (from step 7.3):

| Secret Name | Value | Where to Find |
|------------|-------|---------------|
| `CLERK_DOMAIN` | `your-app.clerk.accounts.dev` | From Clerk dashboard API Keys |
| `CLERK_SECRET_KEY` | `sk_test_...` | From Clerk dashboard API Keys |
| `CLERK_PUBLISHABLE_KEY` | `pk_test_...` | From Clerk dashboard API Keys |

**OpenAI** (from step 5.3):

| Secret Name | Value | Where to Find |
|------------|-------|---------------|
| `OPENAI_API_KEY` | `sk-proj-...` | From OpenAI platform API Keys |

**Telegram** (from step 6.2):

| Secret Name | Value | Where to Find |
|------------|-------|---------------|
| `TELEGRAM_BOT_TOKEN` | `1234567890:ABC...` | From BotFather when you created bot |

**API & Infrastructure** (from step 10.5 - Terraform outputs):

| Secret Name | Value | Where to Find |
|------------|-------|---------------|
| `API_URL` | `https://abc123xyz.execute-api.us-east-1.amazonaws.com/api` | Terraform output: `api_gateway_url` (add `/api` at end) |
| `S3_FRONTEND_BUCKET` | `salesai-frontend-abc123` | Terraform output: `s3_frontend_bucket` |
| `S3_IMAGES_BUCKET` | `salesai-product-images-abc123` | Terraform output: `s3_images_bucket` |
| `CLOUDFRONT_DISTRIBUTION_ID` | `E1234ABCD5678` | Terraform output: `cloudfront_distribution_id` |
| `CLOUDFRONT_DOMAIN` | `d1234567890.cloudfront.net` | Terraform output: `frontend_url` (without https://) |

**Additional Lambda Configuration**:

| Secret Name | Value | Notes |
|------------|-------|-------|
| `LAMBDA_FUNCTION_NAME` | `salesai-dev-api` | Or your actual Lambda function name |

#### 11.3 Verify All Secrets Are Added

After adding all secrets, you should see this list:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY  
AWS_REGION
DB_PASSWORD
CLERK_DOMAIN
CLERK_SECRET_KEY
CLERK_PUBLISHABLE_KEY
OPENAI_API_KEY
TELEGRAM_BOT_TOKEN
API_URL
S3_FRONTEND_BUCKET
S3_IMAGES_BUCKET
CLOUDFRONT_DISTRIBUTION_ID
CLOUDFRONT_DOMAIN
LAMBDA_FUNCTION_NAME
```

**Total: 15 secrets**

#### 11.4 Security Best Practices for Secrets

✅ **DO**:
- Rotate secrets regularly (every 90 days)
- Use different credentials for dev/staging/production
- Enable GitHub's secret scanning
- Review who has access to repository secrets
- Use environment-specific secrets when possible

❌ **DON'T**:
- Never print secrets in GitHub Actions logs
- Don't share repository with untrusted collaborators
- Don't use production credentials in development
- Don't commit secrets to git (ever!)

#### 11.5 Test GitHub Actions Access

You can test that GitHub Actions can access AWS:

1. **Go to "Actions" tab** in your repository
2. **Click "New workflow"**
3. **Set up a test workflow** (we'll replace this with real deployment later)
4. **Click "Start commit"** → "Commit new file"

Or wait until the next step where we'll trigger the actual deployment workflow.

### 12. Deploy Application Code

Now that infrastructure is ready, let's deploy the actual application code (backend and frontend).

#### 12.1 Understanding the Deployment Options

You have two options:

**Option A: Automated via GitHub Actions** (Recommended)
- Push code to GitHub
- GitHub Actions automatically builds and deploys
- Includes health checks and rollback on failure
- Best for continuous deployment

**Option B: Manual Deployment**
- Build and deploy locally using AWS CLI
- More control over the process
- Good for testing or troubleshooting

Let's use Option A (Automated).

#### 12.2 Automated Deployment via GitHub Actions

##### 12.2.1 Prepare Your Repository

1. **Ensure you've committed all changes**:
   ```bash
   git status
   # Check if there are any uncommitted changes
   ```

2. **If you have changes, commit them**:
   ```bash
   git add .
   git commit -m "Initial setup with all configurations"
   ```

3. **Make sure you're on the main branch**:
   ```bash
   git branch
   # Should show * main
   ```

##### 12.2.2 Push to GitHub

```bash
git push origin main
```

This triggers the GitHub Actions workflow automatically!

##### 12.2.3 Monitor Deployment Progress

1. **Go to your GitHub repository**
2. **Click "Actions" tab** (top navigation)
3. **You'll see a workflow running**: "Complete Deployment" or similar
4. **Click on the workflow run** to see details

**Deployment stages** (takes ~15-20 minutes total):

```
📦 Stage 1: Infrastructure (5-10 min)
├─ ✓ Checkout code
├─ ✓ Setup Terraform
├─ ✓ Terraform init
├─ ✓ Terraform plan
└─ ✓ Terraform apply

🐍 Stage 2: Backend Deployment (3-5 min)
├─ ✓ Setup Python
├─ ✓ Install dependencies
├─ ✓ Create Lambda deployment package
├─ ✓ Upload to Lambda
└─ ✓ Update Lambda function

⚛️ Stage 3: Frontend Deployment (5-8 min)
├─ ✓ Setup Node.js
├─ ✓ Install dependencies
├─ ✓ Build React app
├─ ✓ Upload to S3
└─ ✓ Invalidate CloudFront cache

✅ Stage 4: Verification (1-2 min)
├─ ✓ Test API health endpoint
├─ ✓ Verify Lambda function
└─ ✓ Verify frontend accessibility
```

##### 12.2.4 What Each Stage Does

**Infrastructure Stage**:
- Runs Terraform to ensure all AWS resources exist
- Updates any changed resources
- Usually fast (unless adding new resources)

**Backend Stage**:
- Installs Python dependencies
- Packages FastAPI application
- Creates Lambda deployment ZIP
- Uploads to Lambda function
- Updates environment variables

**Frontend Stage**:
- Installs Node.js dependencies
- Builds React application (Vite)
- Optimizes and minifies code
- Uploads to S3 bucket
- Invalidates CloudFront cache (forces fresh content)

**Verification Stage**:
- Tests API `/health` endpoint
- Verifies Lambda function status
- Checks frontend loads correctly

##### 12.2.5 Verify Successful Deployment

After all stages complete (all green checkmarks ✅):

1. **Check the workflow logs**:
   - Click on each stage to see details
   - Look for "Deploy succeeded" messages
   - Note any warnings or errors

2. **Get your deployment URLs**:
   - From workflow output or Terraform outputs:
   ```bash
   cd terraform
   terraform output frontend_url
   terraform output api_gateway_url
   ```

3. **Test API manually**:
   ```bash
   curl https://abc123xyz.execute-api.us-east-1.amazonaws.com/api/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "timestamp": "2024-01-15T10:30:00Z"
   }
   ```

4. **Test frontend**:
   - Open browser
   - Navigate to your CloudFront URL: `https://d1234567890.cloudfront.net`
   - You should see the login page
   - Try signing up / logging in

##### 12.2.6 Manual Deployment Trigger (Optional)

You can also manually trigger deployment from GitHub:

1. **Go to "Actions" tab**
2. **Select "Complete Deployment"** workflow (left sidebar)
3. **Click "Run workflow"** dropdown (right side)
4. **Choose branch**: `main`
5. **Choose deployment options**:
   - Deploy all: Deploys everything
   - Infrastructure only: Just Terraform
   - Backend only: Just Lambda
   - Frontend only: Just React app
6. **Click "Run workflow"** green button
7. **Monitor progress** as described above

##### 12.2.7 Troubleshooting Deployment Failures

**❌ Infrastructure Stage Failed**:

Error: `Error: creating Lambda Function: InvalidParameterValueException`
- ✅ Check IAM permissions
- ✅ Verify secrets are correctly set in GitHub
- ✅ Check Terraform syntax in `terraform/*.tf` files

Error: `Error: timeout while waiting for CloudFront Distribution`
- ✅ This is normal - CloudFront is slow
- ✅ Wait 5-10 more minutes and re-run workflow
- ✅ Or continue to next stages (CloudFront isn't critical for API)

**❌ Backend Stage Failed**:

Error: `ResourceNotFoundException: Function not found`
- ✅ Lambda function wasn't created
- ✅ Check Infrastructure stage completed successfully
- ✅ Verify `LAMBDA_FUNCTION_NAME` secret matches actual function name

Error: `An error occurred (AccessDeniedException)`
- ✅ GitHub Actions doesn't have permission to update Lambda
- ✅ Check IAM user has `lambda:UpdateFunctionCode` permission
- ✅ Review IAM policy from step 1.2

**❌ Frontend Stage Failed**:

Error: `Build failed - Cannot find module '@clerk/clerk-react'`
- ✅ Dependencies not installed correctly
- ✅ Check `package.json` exists in `frontend/` directory
- ✅ Try clearing npm cache and rebuilding

Error: `AccessDenied: Access Denied when writing to S3`
- ✅ GitHub Actions doesn't have S3 write permissions
- ✅ Check IAM user has `s3:PutObject` permission
- ✅ Verify `S3_FRONTEND_BUCKET` secret is correct

Error: `InvalidationBatch failed for CloudFront`
- ✅ Check `CLOUDFRONT_DISTRIBUTION_ID` secret is correct
- ✅ Verify IAM user has `cloudfront:CreateInvalidation` permission

**General Debugging Tips**:
1. **Click on failed stage** to see detailed logs
2. **Look for the red "Error:" messages**
3. **Check the "Set up" step** to verify environment variables
4. **Re-run failed jobs** (click "Re-run failed jobs" button)
5. **Check GitHub secrets** - common cause of failures

📖 **For more deployment options, see [.github/workflows/README.md](.github/workflows/README.md)**

### 13. Manual Deployment (Alternative Method)

If you prefer to deploy manually or need to troubleshoot, follow these steps.

#### 13.1 Deploy Backend to Lambda

##### 13.1.1 Prepare the Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

##### 13.1.2 Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
pip list | grep sqlalchemy
```

##### 13.1.3 Create Lambda Deployment Package

Lambda needs all dependencies packaged together:

```bash
# Create package directory
mkdir -p lambda-package

# Install dependencies to package directory
pip install -r requirements.txt -t lambda-package/

# Copy application code
cp -r app lambda-package/
cp lambda_handler.py lambda-package/

# Optional: Copy alembic for migrations
cp -r alembic lambda-package/
cp alembic.ini lambda-package/

# Navigate to package directory
cd lambda-package

# Create ZIP file
# Windows (PowerShell):
Compress-Archive -Path * -DestinationPath ../lambda-package.zip -Force
# macOS/Linux:
zip -r ../lambda-package.zip .

# Return to backend directory
cd ..

# Verify package size (should be < 50MB unzipped, < 250MB total)
# Windows:
Get-Item lambda-package.zip | Select-Object Name, Length
# macOS/Linux:
ls -lh lambda-package.zip
```

##### 13.1.4 Upload to Lambda

```bash
# Get your Lambda function name
cd ../terraform
terraform output lambda_function_name

# Upload the deployment package
aws lambda update-function-code \
  --function-name salesai-dev-api \
  --zip-file fileb://../backend/lambda-package.zip \
  --publish
```

Expected output:
```json
{
    "FunctionName": "salesai-dev-api",
    "FunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:salesai-dev-api",
    "Runtime": "python3.11",
    "CodeSize": 15234567,
    "LastModified": "2024-01-15T10:30:00.000+0000",
    "State": "Active"
}
```

##### 13.1.5 Verify Backend Deployment

```bash
# Test the API
curl https://your-api-gateway-url.amazonaws.com/api/health

# Or invoke Lambda directly
aws lambda invoke \
  --function-name salesai-dev-api \
  --payload '{"rawPath":"/api/health","requestContext":{"http":{"method":"GET"}}}' \
  response.json

# Check the response
cat response.json
```

#### 13.2 Deploy Frontend to S3

##### 13.2.1 Prepare Frontend Environment

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Or use specific package manager
# yarn install
# pnpm install
```

##### 13.2.2 Configure Environment Variables

Create `.env` file in `frontend/` directory:

```bash
# Create .env file with your API URL
cat > .env << 'EOF'
VITE_API_URL=https://your-api-gateway-url.amazonaws.com/api
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key
EOF

# Windows (PowerShell):
@"
VITE_API_URL=https://your-api-gateway-url.amazonaws.com/api
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key
"@ | Out-File -FilePath .env -Encoding UTF8
```

Replace with your actual values from:
- API URL: Terraform output `api_gateway_url` + `/api`
- Clerk key: From step 7.3

##### 13.2.3 Build Frontend

```bash
# Build for production
npm run build

# This creates a 'dist' directory with optimized files
```

Expected output:
```
vite v4.x.x building for production...
✓ 1234 modules transformed.
dist/index.html                   0.45 kB
dist/assets/index-abc123.css     12.34 kB
dist/assets/index-def456.js      234.56 kB

✓ built in 15.23s
```

##### 13.2.4 Upload to S3

```bash
# Get your S3 bucket name
cd ../terraform
terraform output s3_frontend_bucket

# Sync files to S3 (from frontend directory)
cd ../frontend
aws s3 sync dist/ s3://your-frontend-bucket-name/ --delete

# The --delete flag removes old files that no longer exist
```

Expected output:
```
upload: dist/index.html to s3://salesai-frontend-abc123/index.html
upload: dist/assets/index-abc123.css to s3://salesai-frontend-abc123/assets/index-abc123.css
upload: dist/assets/index-def456.js to s3://salesai-frontend-abc123/assets/index-def456.js
...
```

##### 13.2.5 Invalidate CloudFront Cache

CloudFront caches content, so we need to invalidate it to see changes:

```bash
# Get CloudFront distribution ID
cd ../terraform
terraform output cloudfront_distribution_id

# Create invalidation
aws cloudfront create-invalidation \
  --distribution-id E1234ABCD5678 \
  --paths "/*"

# This invalidates all files
```

Expected output:
```json
{
    "Invalidation": {
        "Id": "I2J3K4L5M6N7O8P9",
        "Status": "InProgress",
        "CreateTime": "2024-01-15T10:30:00Z",
        "InvalidationBatch": {
            "Paths": {
                "Quantity": 1,
                "Items": ["/*"]
            }
        }
    }
}
```

##### 13.2.6 Wait for Invalidation to Complete

```bash
# Check invalidation status
aws cloudfront get-invalidation \
  --distribution-id E1234ABCD5678 \
  --id I2J3K4L5M6N7O8P9

# Wait until Status shows "Completed" (usually 1-5 minutes)
```

##### 13.2.7 Verify Frontend Deployment

1. **Open your browser**
2. **Navigate to CloudFront URL**: `https://d1234567890.cloudfront.net`
3. **Hard refresh** (Ctrl+Shift+R or Cmd+Shift+R) to bypass browser cache
4. **You should see** the login page with Clerk authentication

#### 13.3 Alternative: Deploy with Terraform

You can also update Lambda and trigger redeployment via Terraform:

```bash
cd terraform

# Build backend package first
cd ../backend
# ... follow steps 13.1.3 ...

# Back to terraform
cd ../terraform

# Apply only Lambda changes
terraform apply -target=aws_lambda_function.api

# This uploads the new code automatically
```

### 14. Configure Telegram Bot Webhook

Now that everything is deployed, let's configure your Telegram bot to receive messages.

#### 14.1 Automatic Configuration (Recommended)

The system can automatically configure the webhook when you set your bot token in the dashboard.

1. **Open your frontend** in browser:
   ```
   https://your-cloudfront-domain.cloudfront.net
   ```

2. **Sign up / Log in** using Clerk authentication

3. **Navigate to Settings** (click your profile icon → Settings)

4. **Find "Telegram Bot Configuration" section**

5. **Enter your bot token** (from step 6.2):
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

6. **Click "Save" or "Configure Bot"**

7. **The system will automatically**:
   - Validate the bot token
   - Set the webhook URL
   - Enable the bot
   - Test the connection

8. **You should see**: "✅ Telegram bot configured successfully!"

#### 14.2 Manual Configuration (Alternative)

If automatic configuration fails, configure the webhook manually:

##### 14.2.1 Get Your Webhook URL

```bash
cd terraform
terraform output telegram_webhook_url
```

Should output something like:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/telegram/webhook
```

##### 14.2.2 Set Webhook via Telegram API

```bash
# Replace YOUR_BOT_TOKEN and YOUR_WEBHOOK_URL
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "YOUR_WEBHOOK_URL",
    "allowed_updates": ["message", "callback_query"]
  }'
```

Example:
```bash
curl -X POST "https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://abc123xyz.execute-api.us-east-1.amazonaws.com/telegram/webhook",
    "allowed_updates": ["message", "callback_query"]
  }'
```

Expected response:
```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

##### 14.2.3 Verify Webhook Configuration

```bash
# Check webhook info
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

Expected response:
```json
{
  "ok": true,
  "result": {
    "url": "https://abc123xyz.execute-api.us-east-1.amazonaws.com/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40,
    "allowed_updates": ["message", "callback_query"]
  }
}
```

⚠️ **Troubleshooting webhook issues**:

**"Webhook URL is unreachable"**:
- ✅ Verify API Gateway is deployed and accessible
- ✅ Test the URL: `curl https://your-api-gateway-url.com/telegram/webhook`
- ✅ Check Lambda function logs in CloudWatch
- ✅ Ensure webhook URL uses HTTPS (required by Telegram)

**"Certificate verify failed"**:
- ✅ API Gateway should provide valid SSL certificate automatically
- ✅ Don't use self-signed certificates
- ✅ Verify domain has valid SSL

#### 14.3 Update Bot Token in Application

The bot token must be stored in multiple places:

1. **AWS Secrets Manager** (for Lambda):
   ```bash
   aws secretsmanager update-secret \
     --secret-id salesai-dev-telegram-token \
     --secret-string "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```

2. **Update Lambda environment** (triggers reload):
   ```bash
   aws lambda update-function-configuration \
     --function-name salesai-dev-api \
     --environment "Variables={TELEGRAM_BOT_TOKEN=dummy}"
   
   # Then update with actual value
   aws lambda update-function-configuration \
     --function-name salesai-dev-api \
     --environment "Variables={TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz}"
   ```

   Or let it read from Secrets Manager (preferred - already configured in Terraform)

### 15. Initialize Database

The database schema needs to be created before the application can work.

#### 15.1 Connect to RDS Database

##### 15.1.1 Option A: Via Lambda (Easiest)

The Lambda function can run migrations automatically. Trigger the migration endpoint:

```bash
# Call the migration endpoint
curl -X POST https://your-api-gateway-url.amazonaws.com/api/admin/migrate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

##### 15.1.2 Option B: Via Bastion Host (More Control)

For direct database access, create a bastion host in the public subnet:

1. **Launch EC2 instance** (t2.micro in public subnet)
2. **Install PostgreSQL client**:
   ```bash
   sudo apt update
   sudo apt install postgresql-client
   ```

3. **Connect to RDS**:
   ```bash
   psql -h your-rds-endpoint.rds.amazonaws.com \
        -U salesai_admin \
        -d salesai_db \
        -p 5432
   ```

4. **Enter password** when prompted

5. **Verify connection**:
   ```sql
   \dt  -- List tables
   \l   -- List databases
   ```

##### 15.1.3 Option C: Via Local Alembic (Development)

If running locally with database access:

```bash
cd backend

# Ensure DATABASE_URL is set
export DATABASE_URL="postgresql://user:password@rds-endpoint:5432/dbname"

# Run migrations
alembic upgrade head
```

#### 15.2 Verify Database Schema

Check that tables were created:

```sql
-- Connect via psql
psql -h your-rds-endpoint.rds.amazonaws.com -U salesai_admin -d salesai_db

-- List tables
\dt

-- Should show:
-- users
-- products
-- discounts
-- orders
-- order_items
-- conversations
-- messages
-- alembic_version
```

#### 15.3 Create Test Data (Optional)

Add some initial products for testing:

```sql
-- Insert test products
INSERT INTO products (name, description, price, image_url, stock_quantity, is_active)
VALUES 
  ('Laptop', 'High-performance laptop', 999.99, NULL, 10, true),
  ('Mouse', 'Wireless mouse', 29.99, NULL, 50, true),
  ('Keyboard', 'Mechanical keyboard', 79.99, NULL, 30, true);

-- Verify
SELECT * FROM products;
```

Or add products via the dashboard (preferred).

### 16. Test the Complete System

Now let's test everything end-to-end!

#### 16.1 Test Frontend Access

1. **Open browser** and navigate to your CloudFront URL
2. **You should see** Clerk login page
3. **Sign up** with email or social login
4. **Verify email** if required
5. **You should be redirected** to dashboard

#### 16.2 Add Products

1. **Click "Products"** in sidebar
2. **Click "Add Product"** button
3. **Fill in product details**:
   - Name: "Test Laptop"
   - Description: "A great laptop for testing"
   - Price: 999.99
   - Stock: 10
   - Upload image (optional)
4. **Click "Save"**
5. **Product should appear** in the list

#### 16.3 Configure Discounts

1. **Click "Discounts"** in sidebar
2. **Click "Add Discount"** button
3. **Create a discount**:
   - Type: "Percentage"
   - Value: 10 (for 10% off)
   - Minimum quantity: 2
   - Product: Select "Test Laptop"
4. **Click "Save"**

#### 16.4 Test Telegram Bot

1. **Open Telegram** app
2. **Search for your bot** (the username you created with BotFather)
3. **Start conversation**:
   ```
   /start
   ```

4. **Bot should respond** with welcome message:
   ```
   👋 Welcome to [Your Store Name]!
   
   I'm your AI sales assistant. I can help you:
   • Browse products
   • Get product information
   • Calculate discounts
   • Place orders
   
   What would you like to know about our products?
   ```

5. **Try browsing products**:
   ```
   /browse
   ```

6. **Bot should show** product list with images and prices

7. **Ask about products**:
   ```
   Tell me about the laptop
   ```

8. **Bot should respond** with product details:
   ```
   💻 Test Laptop - $999.99
   
   A great laptop for testing
   
   📦 Stock: 10 available
   
   💰 Special offer: Buy 2 or more and get 10% off!
   
   Would you like to add this to your cart?
   ```

9. **Test discount calculation**:
   ```
   I want to buy 2 laptops
   ```

10. **Bot should calculate**:
    ```
    🛒 Your order:
    • 2x Test Laptop: $999.99 each
    • Subtotal: $1,999.98
    • Discount (10%): -$200.00
    • Total: $1,799.98
    
    Would you like to proceed with the order?
    ```

11. **Complete order** (follow bot prompts)

#### 16.5 Verify Order in Dashboard

1. **Go back to dashboard**
2. **Click "Orders"** in sidebar
3. **You should see** the test order
4. **Click on order** to see details:
   - Customer info (from Telegram)
   - Products ordered
   - Prices and discounts
   - Total amount
   - Order status

#### 16.6 Test AI Agent Boundaries

Try asking off-topic questions to verify guardrails work:

1. **In Telegram, ask**:
   ```
   What's the weather today?
   ```

2. **Bot should redirect**:
   ```
   I'm here specifically to help you with [Your Store Name]'s products. 
   I can assist you with: Test Laptop, and more. 
   
   What would you like to know about our products?
   ```

3. **Try another off-topic question**:
   ```
   Tell me about politics
   ```

4. **Bot should decline**:
   ```
   I can only discuss products from our catalog. 
   
   Would you like to browse our products or get information about a specific item?
   ```

✅ **If all tests pass, your system is fully operational!**

## Local Development

Running the application locally is useful for development and testing before deploying to AWS.

### Prerequisites for Local Development

- Python 3.11 installed
- Node.js 18+ installed
- PostgreSQL installed locally (or use RDS)
- All API keys (Clerk, OpenAI, Telegram) configured

### Option 1: Local Development with Cloud Database (Easier)

Use your deployed RDS database while developing locally.

#### Backend Setup

##### 1. Navigate to Backend Directory

```bash
cd backend
```

##### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

##### 3. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list
```

##### 4. Configure Local Environment Variables

Create `.env` file in `backend/` directory:

```bash
# backend/.env
DATABASE_URL=postgresql://user:password@your-rds-endpoint.rds.amazonaws.com:5432/salesai_db
AWS_REGION=us-east-1
S3_BUCKET_IMAGES=your-product-images-bucket
CLERK_DOMAIN=your-app.clerk.accounts.dev
CLERK_SECRET_KEY=sk_test_your_key
CLERK_PUBLISHABLE_KEY=pk_test_your_key
OPENAI_API_KEY=sk-proj-your_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_URL=http://localhost:8000/api/telegram/webhook
```

⚠️ **Important**: Use the same values from your deployed `.env` file.

##### 5. Run Database Migrations (if needed)

```bash
# Apply any pending migrations
alembic upgrade head

# Or create new migration after model changes
alembic revision --autogenerate -m "Description of changes"
```

##### 6. Start Development Server

```bash
# Run with auto-reload (restarts on code changes)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

##### 7. Test Backend API

Open another terminal and test:

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","database":"connected","timestamp":"..."}

# Test products endpoint (requires auth)
curl http://localhost:8000/api/products

# View API documentation
# Open browser: http://localhost:8000/docs
```

#### Frontend Setup

##### 1. Open New Terminal (keep backend running)

```bash
# Navigate to frontend directory
cd frontend
```

##### 2. Install Dependencies

```bash
# Install packages
npm install

# Or use yarn/pnpm
yarn install
pnpm install
```

##### 3. Configure Frontend Environment

Create `.env` file in `frontend/` directory:

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000/api
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key
```

⚠️ **Note**: Using local API (localhost:8000), not the deployed API Gateway.

##### 4. Start Development Server

```bash
# Run Vite dev server
npm run dev

# Or specify port
npm run dev -- --port 5173
```

Expected output:
```
  VITE v4.x.x  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
  ➜  press h to show help
```

##### 5. Open in Browser

Navigate to: `http://localhost:5173`

You should see:
- Clerk login page
- Can sign up / sign in
- Dashboard loads after authentication
- Can add/edit products
- Can configure discounts

##### 6. Configure CORS for Local Development

If you see CORS errors, update `backend/app/main.py`:

```python
# Add localhost to allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://your-cloudfront-domain.cloudfront.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Testing Telegram Bot Locally

To test Telegram bot locally, you need to expose your local server to the internet:

##### Option A: Using ngrok (Recommended)

1. **Install ngrok**: [ngrok.com/download](https://ngrok.com/download)

2. **Start ngrok tunnel**:
   ```bash
   ngrok http 8000
   ```

3. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

4. **Update Telegram webhook**:
   ```bash
   curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://abc123.ngrok.io/telegram/webhook"}'
   ```

5. **Test the bot** in Telegram

6. **View requests** in ngrok dashboard: `http://127.0.0.1:4040`

##### Option B: Using localtunnel

```bash
# Install localtunnel
npm install -g localtunnel

# Start tunnel
lt --port 8000

# Use the provided URL for webhook
```

⚠️ **Remember**: Change webhook back to production URL after local testing!

### Option 2: Fully Local Development (Advanced)

Run everything locally including PostgreSQL.

#### 1. Install PostgreSQL Locally

**Windows**:
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Run installer
- Remember the password you set for `postgres` user

**macOS**:
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### 2. Create Local Database

```bash
# Connect as postgres user
# Windows/macOS:
psql -U postgres

# Linux:
sudo -u postgres psql

# Create database and user
CREATE DATABASE salesai_db;
CREATE USER salesai_admin WITH PASSWORD 'local_dev_password';
GRANT ALL PRIVILEGES ON DATABASE salesai_db TO salesai_admin;

# Exit
\q
```

#### 3. Update DATABASE_URL

In `backend/.env`:
```
DATABASE_URL=postgresql://salesai_admin:local_dev_password@localhost:5432/salesai_db
```

#### 4. Run Migrations

```bash
cd backend
alembic upgrade head
```

#### 5. Follow Backend/Frontend Setup

Continue with steps from Option 1 above.

### Development Workflow

#### Making Backend Changes

1. **Edit code** in `backend/app/` directory
2. **Server auto-reloads** (if using `--reload` flag)
3. **Test changes** using curl or Swagger UI (`http://localhost:8000/docs`)
4. **Check logs** in terminal for errors

#### Making Frontend Changes

1. **Edit code** in `frontend/src/` directory
2. **Vite hot-reloads** automatically
3. **Browser updates** instantly
4. **Check browser console** for errors (F12)

#### Making Database Changes

1. **Edit models** in `backend/app/models/`
2. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "Add new field to User"
   ```
3. **Review migration** in `backend/alembic/versions/`
4. **Apply migration**:
   ```bash
   alembic upgrade head
   ```
5. **Test changes** in API

### Useful Development Commands

#### Backend

```bash
# Run with debug logging
uvicorn app.main:app --reload --log-level debug

# Run on different port
uvicorn app.main:app --reload --port 9000

# Check Python code quality
flake8 app/
black app/  # Format code
mypy app/   # Type checking

# Run tests
pytest tests/ -v
pytest tests/ --cov=app  # With coverage
```

#### Frontend

```bash
# Run dev server
npm run dev

# Build for production (test build locally)
npm run build
npm run preview  # Preview production build

# Lint code
npm run lint
npm run lint:fix  # Auto-fix issues

# Type check
npm run type-check

# Format code
npm run format
```

### Debugging Tips

#### Backend Debugging

1. **Add print statements**:
   ```python
   print(f"Debug: user_id = {user_id}")
   ```

2. **Use pdb (Python debugger)**:
   ```python
   import pdb; pdb.set_trace()
   ```

3. **Check logs**:
   - Terminal where uvicorn is running
   - Look for stack traces

4. **Test with Swagger UI**:
   - Open `http://localhost:8000/docs`
   - Try API endpoints interactively
   - See request/response details

#### Frontend Debugging

1. **Browser DevTools** (F12):
   - Console: See errors and logs
   - Network: See API requests/responses
   - Elements: Inspect DOM
   - React DevTools: Inspect components

2. **Add console.log**:
   ```javascript
   console.log('Debug:', variable);
   ```

3. **React Query DevTools**:
   - Automatically enabled in development
   - See query status, cache, etc.

4. **Clerk DevTools**:
   - Check authentication status
   - View user session

### Environment Switching

To switch between local and deployed environments:

1. **Create multiple .env files**:
   ```
   frontend/.env.local
   frontend/.env.production
   ```

2. **Switch by renaming**:
   ```bash
   cp .env.local .env
   # or
   cp .env.production .env
   ```

3. **Or use env variables**:
   ```bash
   VITE_API_URL=http://localhost:8000/api npm run dev
   ```

### Running Tests

#### Backend Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_products.py -v

# Run specific test function
pytest tests/test_products.py::test_create_product -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser

# Run tests with output
pytest tests/ -v -s

# Run tests in parallel (faster)
pytest tests/ -n auto
```

#### Frontend Tests

```bash
cd frontend

# Run tests
npm run test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

#### Integration Tests

```bash
# Test entire API flow
cd backend
pytest tests/integration/ -v

# Test with real database (use test database!)
DATABASE_URL=postgresql://user:pass@localhost:5432/test_db pytest tests/
```

## Database Migrations

### Understanding Alembic Migrations

Alembic is a database migration tool that:
- Tracks schema changes over time
- Allows upgrading/downgrading database
- Generates migrations automatically from model changes
- Keeps database in sync across environments

### Migration Workflow

#### 1. Make Changes to Models

Edit files in `backend/app/models/`:

```python
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    # NEW FIELD:
    phone_number = Column(String, nullable=True)
```

#### 2. Generate Migration

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add phone_number to users"
```

This creates a new file in `backend/alembic/versions/` like:
```
abc123def456_add_phone_number_to_users.py
```

#### 3. Review Migration

Open the generated file and verify:

```python
def upgrade():
    # Add column
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))

def downgrade():
    # Remove column
    op.drop_column('users', 'phone_number')
```

✅ **Always review auto-generated migrations!** Sometimes they need manual adjustment.

#### 4. Apply Migration

```bash
# Apply all pending migrations
alembic upgrade head

# Or apply specific number of migrations
alembic upgrade +1  # Apply next migration
alembic upgrade +2  # Apply next 2 migrations
```

#### 5. Verify Changes

```bash
# Connect to database
psql -h your-db-host -U salesai_admin -d salesai_db

# Check table structure
\d users

# You should see the new phone_number column
```

### Common Migration Operations

#### Add Column

```python
# In migration file
def upgrade():
    op.add_column('products', 
        sa.Column('discount_price', sa.Numeric(10, 2), nullable=True))

def downgrade():
    op.drop_column('products', 'discount_price')
```

#### Remove Column

```python
def upgrade():
    op.drop_column('products', 'old_field')

def downgrade():
    op.add_column('products', 
        sa.Column('old_field', sa.String(), nullable=True))
```

#### Rename Column

```python
def upgrade():
    op.alter_column('products', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('products', 'new_name', new_column_name='old_name')
```

#### Add Index

```python
def upgrade():
    op.create_index('idx_product_name', 'products', ['name'])

def downgrade():
    op.drop_index('idx_product_name', table_name='products')
```

#### Create New Table

```python
def upgrade():
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id')),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True)
    )

def downgrade():
    op.drop_table('reviews')
```

### Rolling Back Migrations

#### Downgrade Last Migration

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123def456

# Rollback all migrations (DANGEROUS!)
alembic downgrade base
```

#### View Migration History

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show migration history with details
alembic history --verbose
```

### Migration Best Practices

✅ **DO**:
- Always review auto-generated migrations
- Test migrations on development database first
- Write reversible migrations (both upgrade and downgrade)
- Add descriptive migration messages
- Commit migrations to git
- Run migrations before deploying code changes

❌ **DON'T**:
- Don't edit applied migrations (create new one instead)
- Don't delete migration files
- Don't skip migrations
- Don't run migrations directly on production without testing
- Don't forget to backup database before migrations

### Deploying Migrations to Production

#### Option 1: Via Lambda Endpoint (Automated)

```bash
# Call migration endpoint after deployment
curl -X POST https://your-api-gateway-url.amazonaws.com/api/admin/migrate \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Option 2: Via Bastion Host (Manual)

```bash
# SSH to bastion host
ssh -i your-key.pem ec2-user@bastion-ip

# Install Python and dependencies
sudo yum install python3 git
git clone your-repo
cd your-repo/backend
pip3 install -r requirements.txt

# Set DATABASE_URL
export DATABASE_URL="postgresql://user:pass@rds-endpoint:5432/db"

# Run migrations
alembic upgrade head
```

#### Option 3: Via GitHub Actions (Recommended)

Add to your deployment workflow:

```yaml
- name: Run Database Migrations
  run: |
    cd backend
    pip install -r requirements.txt
    alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Troubleshooting Migrations

**Error: "Target database is not up to date"**
```bash
# Check current version
alembic current

# Check pending migrations
alembic history

# Apply pending migrations
alembic upgrade head
```

**Error: "Can't locate revision abc123"**
- ✅ Migration file is missing from `alembic/versions/`
- ✅ Pull latest migrations from git
- ✅ Check if file was accidentally deleted

**Error: "Multiple head revisions present"**
- ✅ Multiple branches in migration history
- ✅ Merge migrations:
```bash
alembic merge heads -m "Merge migrations"
alembic upgrade head
```

**Error: Column already exists**
- ✅ Migration was partially applied
- ✅ Either rollback or manually fix database to match expected state
- ✅ Then mark migration as applied:
```bash
alembic stamp head
```

**Want to start fresh (development only!)**
```bash
# Drop all tables
psql -h localhost -U user -d db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run all migrations
alembic upgrade head
```

## Project Structure

```
salesai/
├── backend/                   # Python FastAPI backend
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── auth.py           # Authentication
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   └── main.py           # FastAPI app
│   ├── tests/                # Test files
│   ├── requirements.txt      # Python dependencies
│   └── lambda_handler.py     # Lambda entry point
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── lib/              # Utilities and API client
│   │   ├── store/            # State management
│   │   ├── types/            # TypeScript types
│   │   └── main.tsx          # App entry point
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite configuration
├── terraform/                 # Infrastructure as Code
│   ├── main.tf               # Main Terraform config
│   ├── variables.tf          # Variable definitions
│   ├── vpc.tf                # VPC resources
│   ├── rds.tf                # Database resources
│   ├── lambda.tf             # Lambda functions
│   ├── api_gateway.tf        # API Gateway
│   ├── s3.tf                 # S3 buckets
│   └── cloudfront.tf         # CloudFront distribution
└── .github/
    └── workflows/            # CI/CD pipelines
        ├── deploy.yml        # Main deployment workflow (use this!)
        ├── README.md         # Deployment documentation
        └── modules/          # Individual workflow components
            ├── terraform.yml
            ├── backend-deploy.yml
            └── frontend-deploy.yml
```

## Documentation

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Deploy in 30 minutes (start here!)
- **[.env.setup.md](.env.setup.md)** - Environment variables setup guide
- **[README.md](README.md)** - Main documentation (you're here!)

### Deployment
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Automated deployment guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed manual deployment instructions  
- **[.github/workflows/README.md](.github/workflows/README.md)** - GitHub Actions workflows

### Authentication & Security
- **[CLERK_SETUP.md](CLERK_SETUP.md)** - Clerk authentication setup
- **[AUTHENTICATION.md](AUTHENTICATION.md)** - Auth architecture details

### Features & Guides
- **[AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md)** - AI agent behavior & guardrails

### Contributing
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines

## Key Components

### Authentication (Clerk)

This application uses Clerk for authentication, providing:
- **Multiple sign-in methods**: Email, Google, GitHub, and more
- **User management dashboard**: View and manage users
- **Security features**: 2FA, session management, brute force protection
- **No password storage**: Secure authentication without storing passwords
- **Automatic user creation**: Users created in database on first login

📖 **For setup instructions, see [CLERK_SETUP.md](CLERK_SETUP.md)**
📖 **For architecture details, see [AUTHENTICATION.md](AUTHENTICATION.md)**

### AI Agent Boundaries

The AI sales agent is designed with strict boundaries to ensure it ONLY discusses products from your catalog:

**What the agent WILL do:**
- Answer questions about products in your catalog
- Show product details, prices, and images
- Calculate discounts and totals
- Process orders for your products
- Help customers make purchase decisions

**What the agent WILL NOT do:**
- Discuss products not in your catalog
- Engage in off-topic conversations (politics, news, sports, etc.)
- Provide general knowledge or advice
- Compare to competitors
- Discuss topics outside of your specific products

**How it works:**
1. **System Prompt**: Explicitly instructs the AI to stay focused on catalog products
2. **Response Validation**: Every response is checked for off-topic content
3. **Fallback Responses**: If the AI strays off-topic, it's automatically replaced with a redirect to your products
4. **Keyword Detection**: Monitors for common off-topic keywords (politics, health advice, news, etc.)

**Example Interactions:**

Customer: "Tell me about your laptops"
Agent: ✅ "We have high-performance laptops for $999.99..."

Customer: "What's the weather like today?"
Agent: ✅ "I'm here specifically to help you with Test Store's products. I can assist you with: Laptop, Mouse, and more. What would you like to know about our products?"

Customer: "Tell me about politics"
Agent: ✅ Automatically redirected to discuss products

This ensures your AI agent stays professional, focused, and provides a consistent brand experience.

📖 **For detailed information about the AI agent, see [AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md)**

### Discount Engine

The discount engine supports three types of discounts:

1. **Percentage Discount**: E.g., "10% off when buying 3 or more"
2. **Fixed Discount**: E.g., "$20 off when buying 5 or more"
3. **Buy X Get Y**: E.g., "Buy 2 get 1 free"

Discounts are automatically calculated and the best discount is always applied.

### AI Agent

The AI agent uses OpenAI's GPT-4 with function calling to:
- Browse products
- Show product images
- Calculate prices with discounts
- Add items to cart
- Collect customer information
- Create orders

**Strict Guardrails:**
- The agent ONLY discusses products in the seller's catalog
- Automatically declines off-topic conversations (politics, news, general knowledge, etc.)
- Redirects customers back to product discussions
- Validates all responses to ensure they stay on-topic
- Uses a fallback response if the AI tries to go off-topic

### Telegram Bot

The bot operates via webhooks (no polling) for optimal performance in Lambda. It:
- Routes messages to the AI agent
- Sends product images
- Maintains conversation context
- Handles commands (`/start`, `/browse`, `/cart`)

## Environment Variables

### Backend

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
AWS_REGION=us-east-1
S3_BUCKET_IMAGES=salesai-product-images
CLERK_DOMAIN=your-app.clerk.accounts.dev
CLERK_SECRET_KEY=sk_test_your-key
CLERK_PUBLISHABLE_KEY=pk_test_your-key
OPENAI_API_KEY=sk-your-openai-key
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_URL=https://your-api-url/api/telegram/webhook
```

### Frontend

```
VITE_API_URL=https://your-api-gateway-url.amazonaws.com/api
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your-key
```

## Security Best Practices

### Authentication & Authorization

#### Clerk Security

✅ **Implemented**:
- JWT-based authentication
- Secure session management
- Email verification
- Password strength requirements
- Brute force protection

**Additional Recommendations**:

1. **Enable 2FA (Two-Factor Authentication)**:
   - Go to Clerk dashboard → User & Authentication
   - Enable "Two-factor authentication"
   - Users can enable 2FA in their profile

2. **Configure session timeout**:
   - Clerk dashboard → Sessions
   - Set appropriate session lifetime (default: 7 days)
   - Enable "Inactivity timeout" for sensitive applications

3. **Review user activity**:
   - Clerk dashboard → Users
   - Monitor sign-in activity
   - Check for suspicious patterns

#### API Security

✅ **Implemented**:
- All endpoints protected by Clerk JWT validation
- Telegram webhook has token validation
- CORS configured with specific origins

**Additional Recommendations**:

1. **Add rate limiting per user**:
   ```python
   # backend/app/middleware/rate_limit.py
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.get("/api/products")
   @limiter.limit("100/minute")
   async def get_products():
       pass
   ```

2. **Add API key for admin endpoints**:
   ```python
   # Require admin role for sensitive operations
   @app.post("/api/admin/migrate")
   async def run_migrations(current_user: User = Depends(require_admin)):
       pass
   ```

3. **Implement request validation**:
   ```python
   # Use Pydantic for input validation
   class ProductCreate(BaseModel):
       name: str = Field(..., min_length=1, max_length=200)
       price: Decimal = Field(..., gt=0, le=999999.99)
   ```

### AWS Security

#### IAM Best Practices

✅ **Implemented**:
- Separate IAM user for deployment
- Lambda execution role with minimal permissions
- RDS in private subnet

**Additional Recommendations**:

1. **Rotate access keys regularly**:
   ```bash
   # Create new key
   aws iam create-access-key --user-name aiengineer
   
   # Test new key
   # Update GitHub secrets and .env
   
   # Delete old key
   aws iam delete-access-key --user-name aiengineer --access-key-id OLD_KEY
   ```

2. **Enable MFA for IAM users**:
   ```bash
   aws iam enable-mfa-device \
     --user-name aiengineer \
     --serial-number arn:aws:iam::ACCOUNT_ID:mfa/aiengineer \
     --authentication-code1 123456 \
     --authentication-code2 789012
   ```

3. **Use IAM roles instead of access keys for EC2**:
   - Attach IAM role to EC2 instances
   - No need to store credentials on instance

4. **Review IAM policies regularly**:
   ```bash
   # List policies
   aws iam list-attached-user-policies --user-name aiengineer
   
   # Review policy permissions
   aws iam get-policy-version --policy-arn ARN --version-id v1
   ```

#### Network Security

✅ **Implemented**:
- VPC with public and private subnets
- Security groups restricting access
- NAT Gateway for Lambda internet access

**Additional Recommendations**:

1. **Enable VPC Flow Logs**:
   ```bash
   aws ec2 create-flow-logs \
     --resource-type VPC \
     --resource-ids vpc-xxxxx \
     --traffic-type ALL \
     --log-destination-type cloud-watch-logs \
     --log-group-name /aws/vpc/salesai-dev
   ```

2. **Use AWS WAF for API Gateway** (additional cost):
   - Protects against SQL injection, XSS
   - Rate limiting
   - IP allowlist/blocklist

3. **Enable GuardDuty** (threat detection):
   ```bash
   aws guardduty create-detector --enable
   ```

#### Data Security

✅ **Implemented**:
- RDS encryption at rest
- HTTPS enforced via CloudFront
- Secrets in Secrets Manager

**Additional Recommendations**:

1. **Enable RDS automated backups**:
   ```bash
   aws rds modify-db-instance \
     --db-instance-identifier salesai-dev-db \
     --backup-retention-period 7 \
     --preferred-backup-window "03:00-04:00"
   ```

2. **Enable RDS encryption** (if not already):
   ```bash
   # For new instances
   aws rds create-db-instance \
     --storage-encrypted \
     --kms-key-id alias/aws/rds
   ```

3. **Enable S3 versioning** (for rollback):
   ```bash
   aws s3api put-bucket-versioning \
     --bucket your-frontend-bucket \
     --versioning-configuration Status=Enabled
   ```

4. **Enable S3 server-side encryption**:
   ```bash
   aws s3api put-bucket-encryption \
     --bucket your-images-bucket \
     --server-side-encryption-configuration '{
       "Rules": [{
         "ApplyServerSideEncryptionByDefault": {
           "SSEAlgorithm": "AES256"
         }
       }]
     }'
   ```

### Application Security

#### Input Validation

1. **Validate all user inputs**:
   ```python
   # Use Pydantic models for validation
   class OrderCreate(BaseModel):
       product_id: int = Field(..., gt=0)
       quantity: int = Field(..., gt=0, le=100)
       customer_email: EmailStr
   ```

2. **Sanitize data before storing**:
   ```python
   from bleach import clean
   
   safe_description = clean(user_input, tags=[], strip=True)
   ```

3. **Use parameterized queries** (SQLAlchemy does this automatically):
   ```python
   # ✅ Safe (parameterized)
   db.query(User).filter(User.email == email).first()
   
   # ❌ Unsafe (SQL injection risk)
   db.execute(f"SELECT * FROM users WHERE email = '{email}'")
   ```

#### Secrets Management

1. **Never commit secrets to git**:
   ```bash
   # Add to .gitignore
   .env
   .env.*
   *.pem
   secrets.json
   ```

2. **Use environment variables**:
   ```python
   import os
   API_KEY = os.getenv("API_KEY")  # ✅ Good
   API_KEY = "sk-123456"  # ❌ Bad
   ```

3. **Rotate secrets regularly**:
   - Database passwords: Every 90 days
   - API keys: Every 180 days
   - Access tokens: Every 30 days

4. **Use AWS Secrets Manager for sensitive data**:
   ```python
   import boto3
   client = boto3.client('secretsmanager')
   secret = client.get_secret_value(SecretId='db-password')
   ```

### Monitoring & Logging

1. **Enable CloudWatch Logs** (already configured):
   - Lambda function logs
   - API Gateway access logs
   - VPC Flow Logs

2. **Set up CloudWatch Alarms**:
   ```bash
   # Alert on Lambda errors
   aws cloudwatch put-metric-alarm \
     --alarm-name salesai-lambda-errors \
     --alarm-description "Alert on Lambda errors" \
     --metric-name Errors \
     --namespace AWS/Lambda \
     --statistic Sum \
     --period 300 \
     --threshold 10 \
     --comparison-operator GreaterThanThreshold \
     --evaluation-periods 1
   ```

3. **Log security events**:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   # Log authentication failures
   logger.warning(f"Failed login attempt: {email}")
   
   # Log suspicious activity
   logger.error(f"SQL injection attempt detected: {query}")
   ```

4. **Review logs regularly**:
   ```bash
   # Search for errors
   aws logs filter-log-events \
     --log-group-name /aws/lambda/salesai-dev-api \
     --filter-pattern "ERROR"
   ```

### Compliance & Privacy

1. **GDPR Compliance** (if serving EU users):
   - Add privacy policy
   - Implement data export
   - Implement right to deletion
   - Cookie consent banner

2. **Data retention policies**:
   ```python
   # Delete old data periodically
   from datetime import datetime, timedelta
   
   cutoff_date = datetime.now() - timedelta(days=365)
   db.query(Message).filter(Message.created_at < cutoff_date).delete()
   ```

3. **User data protection**:
   - Don't log sensitive data (passwords, credit cards)
   - Hash sensitive fields
   - Encrypt PII (Personally Identifiable Information)

### Security Checklist Before Production

- [ ] Enable 2FA for AWS root account
- [ ] Enable MFA for IAM users
- [ ] Rotate all access keys
- [ ] Enable RDS automated backups
- [ ] Enable RDS Multi-AZ (for high availability)
- [ ] Enable VPC Flow Logs
- [ ] Set up CloudWatch alarms
- [ ] Review security groups (least privilege)
- [ ] Enable S3 versioning
- [ ] Enable S3 encryption
- [ ] Configure WAF rules (if using)
- [ ] Review Clerk authentication settings
- [ ] Set up monitoring and alerting
- [ ] Enable GuardDuty
- [ ] Document incident response plan
- [ ] Configure automatic security patching
- [ ] Set up log retention policies
- [ ] Review and test backup restoration
- [ ] Perform security audit
- [ ] Set up rate limiting
- [ ] Enable API logging

## Cost Estimation & Optimization

### Monthly Cost Breakdown (Development Environment)

#### AWS Resources

| Service | Configuration | Est. Monthly Cost | Notes |
|---------|--------------|-------------------|-------|
| **RDS PostgreSQL** | db.t3.micro, 20GB storage | $15-20 | Can be reduced with Reserved Instances |
| **Lambda** | 512MB, 100K requests | $5-10 | First 1M requests/month free |
| **NAT Gateway** | 1 NAT in single AZ | $32-40 | Largest cost; consider alternatives |
| **API Gateway** | HTTP API, 100K requests | $1-3.50 | First 1M requests free for 12 months |
| **S3 Storage** | 5GB + requests | $1-2 | Very cheap for static files |
| **CloudFront** | 10GB transfer | $1-2 | First 1TB/month free for 12 months |
| **Secrets Manager** | 5 secrets | $2-3 | $0.40 per secret per month |
| **VPC** | Standard VPC resources | Free | No charge for VPC itself |
| **CloudWatch Logs** | 5GB logs + queries | $2-5 | Can add up with verbose logging |

**Development Total: $57-85/month**

**First Year (with free tier): $30-50/month**

#### Production Environment (Higher Traffic)

| Service | Configuration | Est. Monthly Cost |
|---------|--------------|-------------------|
| **RDS PostgreSQL** | db.t3.small, 100GB, Multi-AZ | $50-80 |
| **Lambda** | 1024MB, 1M requests | $20-40 |
| **NAT Gateway** | 2 NATs (HA) | $64-80 |
| **API Gateway** | HTTP API, 1M requests | $3.50-10 |
| **S3 + CloudFront** | 100GB transfer | $10-15 |
| **WAF** (optional) | Web ACL + rules | $5-20 |
| **Other** | Logs, Secrets, etc. | $5-10 |

**Production Total: $157-255/month**

#### External Services

| Service | Usage | Est. Monthly Cost |
|---------|-------|-------------------|
| **OpenAI API** | GPT-4, ~10K messages | $30-100 | Varies greatly with usage |
| **Clerk** | Up to 10K MAU | Free | $25/month for 10K-100K MAU |
| **Telegram** | Unlimited messages | Free | Always free |

**External Services Total: $30-125/month**

### Total Estimated Costs

- **Development**: $87-210/month
- **Production (moderate traffic)**: $187-380/month
- **Production (high traffic)**: $300-600/month

### Cost Optimization Strategies

#### High-Impact Optimizations (Save $30-40/month)

##### 1. Replace NAT Gateway with VPC Endpoints (Save ~$32/month)

**Current**: NAT Gateway allows Lambda to access internet ($32/month)

**Alternative**: Use VPC Endpoints for AWS services (free/minimal cost)

```hcl
# terraform/vpc.tf
# Add VPC Endpoints for S3 and Secrets Manager
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.s3"
  route_table_ids = [aws_route_table.private.id]
}

resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
}
```

**Limitations**:
- Lambda can only access AWS services via endpoints
- Can't call external APIs (like OpenAI, Telegram)
- Consider if you need internet access

**Best approach**: Hybrid
- Use VPC Endpoints for AWS services (S3, Secrets Manager, RDS)
- Remove NAT Gateway if you move OpenAI calls to a separate Lambda in public subnet
- Or use API Gateway to proxy external API calls

##### 2. Use Reserved Instances for RDS (Save ~30-40%)

```bash
# Purchase 1-year Reserved Instance
aws rds purchase-reserved-db-instances-offering \
  --reserved-db-instances-offering-id offering-id \
  --db-instance-count 1

# Savings:
# db.t3.micro: $15/month → $10/month (save $5/month)
# db.t3.small: $50/month → $30/month (save $20/month)
```

##### 3. Right-Size Lambda Memory (Save ~$5-10/month)

```bash
# Test different memory sizes
# 512MB: Slow but cheap
# 1024MB: 2x faster, 2x cost
# 2048MB: 4x faster, 4x cost

# Find the sweet spot:
aws lambda update-function-configuration \
  --function-name salesai-dev-api \
  --memory-size 768  # Good balance
```

**Pro tip**: Higher memory = more CPU = faster execution = potentially lower cost

#### Medium-Impact Optimizations (Save $10-20/month)

##### 4. Optimize Lambda Package Size

```bash
# Smaller package = faster cold starts = lower costs

# Current size: 50MB
# Optimized size: 15MB

# Remove unnecessary dependencies
# Use Lambda Layers for common libraries
# Compress assets
```

##### 5. Use CloudFront Caching Effectively

```hcl
# Increase cache TTL to reduce origin requests
default_cache_behavior {
  min_ttl     = 0
  default_ttl = 86400    # 24 hours (was 3600)
  max_ttl     = 31536000 # 1 year
}
```

##### 6. Reduce CloudWatch Logs Retention

```bash
# Default: Infinite retention (costs add up)
# Recommended: 30 days for production, 7 days for dev

aws logs put-retention-policy \
  --log-group-name /aws/lambda/salesai-dev-api \
  --retention-in-days 7
```

##### 7. Use S3 Intelligent-Tiering

```bash
# Automatically moves infrequently accessed objects to cheaper storage
aws s3api put-bucket-intelligent-tiering-configuration \
  --bucket your-images-bucket \
  --id rule1 \
  --intelligent-tiering-configuration '{
    "Id": "rule1",
    "Status": "Enabled",
    "Tierings": [{
      "Days": 90,
      "AccessTier": "ARCHIVE_ACCESS"
    }]
  }'
```

#### Low-Impact Optimizations (Save $5-10/month)

##### 8. Optimize Database Queries

```python
# Use connection pooling
# Add indexes to frequently queried columns
# Use select_related/joinedload to avoid N+1 queries
# Implement caching for frequently accessed data

from functools import lru_cache

@lru_cache(maxsize=128)
def get_products():
    return db.query(Product).filter(Product.is_active == True).all()
```

##### 9. Compress Assets

```bash
# Enable gzip/brotli compression in CloudFront
# Reduces transfer costs

# In CloudFront distribution:
compress_enabled = true
```

##### 10. Use DynamoDB Instead of RDS (Advanced)

**Only if**:
- Simple key-value queries
- No complex joins needed
- High read/write throughput

**Cost comparison**:
- RDS db.t3.micro: $15/month
- DynamoDB On-Demand: $1.25 per million reads, $6.25 per million writes
- DynamoDB could be cheaper for low-traffic apps

### Free Tier Benefits (First 12 Months)

AWS Free Tier includes:
- ✅ 750 hours/month of db.t3.micro RDS (single-AZ)
- ✅ 1M Lambda requests + 400K GB-seconds compute/month
- ✅ 1M API Gateway requests/month
- ✅ 5GB S3 storage
- ✅ 1TB CloudFront data transfer out/month

**With free tier, first year cost: $30-50/month** (mainly NAT Gateway)

### Cost Monitoring & Alerts

#### Set Up Cost Alerts

1. **Enable Cost Explorer**:
   - AWS Console → Cost Management → Cost Explorer
   - View spending by service

2. **Create Budget Alert**:
   ```bash
   aws budgets create-budget \
     --account-id YOUR_ACCOUNT_ID \
     --budget '{
       "BudgetName": "SalesAI Monthly Budget",
       "BudgetLimit": {
         "Amount": "100",
         "Unit": "USD"
       },
       "TimeUnit": "MONTHLY",
       "BudgetType": "COST"
     }' \
     --notifications-with-subscribers '[{
       "Notification": {
         "NotificationType": "ACTUAL",
         "ComparisonOperator": "GREATER_THAN",
         "Threshold": 80
       },
       "Subscribers": [{
         "SubscriptionType": "EMAIL",
         "Address": "your-email@example.com"
       }]
     }]'
   ```

3. **Monitor with Tags**:
   ```hcl
   # Tag all resources for cost tracking
   tags = {
     Project     = "salesai"
     Environment = "dev"
     CostCenter  = "engineering"
   }
   ```

4. **Review Cost and Usage Reports**:
   - Enable detailed billing reports
   - Export to S3 for analysis
   - Use tools like AWS Cost Intelligence Dashboard

#### Track OpenAI API Costs

1. **Set usage limits** in OpenAI dashboard:
   - Hard limit: $50/month
   - Soft limit: $25/month (sends alert)

2. **Monitor usage**:
   - Visit [platform.openai.com/usage](https://platform.openai.com/usage)
   - Check daily spending
   - Review token usage per request

3. **Optimize OpenAI costs**:
   ```python
   # Use GPT-3.5-turbo instead of GPT-4 for simple queries
   # GPT-4: $0.03/1K input tokens, $0.06/1K output tokens
   # GPT-3.5-turbo: $0.0005/1K input tokens, $0.0015/1K output tokens
   
   model = "gpt-3.5-turbo" if simple_query else "gpt-4"
   ```

### Cost-Effective Architecture Alternatives

#### Serverless-Only (Lowest Cost)

Replace RDS with DynamoDB:
- RDS: $15-80/month
- DynamoDB: $0-10/month for low traffic

**Savings**: $10-70/month

**Trade-offs**:
- More complex queries
- No SQL features (joins, transactions)
- Need to refactor application code

#### Containerized with ECS Fargate (Predictable Cost)

Replace Lambda with ECS Fargate:
- Lambda: Variable, pay per request
- Fargate: Fixed, pay for running time

**Good for**:
- Consistent traffic
- Long-running processes
- Predictable costs

**Cost**: $30-50/month for 1 Fargate task (0.25 vCPU, 0.5 GB)

#### Monolithic EC2 (Maximum Control)

Replace Lambda + RDS with single EC2 instance:
- t3.small: $15-20/month
- Install PostgreSQL on same instance

**Savings**: $30-40/month

**Trade-offs**:
- Less scalable
- Need to manage server
- No auto-scaling
- Single point of failure

## Troubleshooting

Comprehensive troubleshooting guide for common issues.

### AWS Infrastructure Issues

#### IAM Permission Errors

**Error**: `AccessDenied` or `UnauthorizedOperation` when running Terraform

**Symptoms**:
```
Error: creating EC2 VPC: UnauthorizedOperation: You are not authorized to perform this operation
Error: AccessDenied: User is not authorized to perform: lambda:CreateFunction
```

**Solutions**:
1. **Verify IAM user has correct policies**:
   ```bash
   # Check user's attached policies
   aws iam list-attached-user-policies --user-name aiengineer
   ```

2. **Add missing permissions** (see step 1.2 for policy)

3. **Check AWS credentials are configured**:
   ```bash
   aws sts get-caller-identity
   # Should show your IAM user, not an error
   ```

4. **Verify credentials in use**:
   ```bash
   # Windows (PowerShell):
   $env:AWS_ACCESS_KEY_ID
   $env:AWS_SECRET_ACCESS_KEY
   
   # macOS/Linux:
   echo $AWS_ACCESS_KEY_ID
   echo $AWS_SECRET_ACCESS_KEY
   ```

5. **Re-configure AWS CLI**:
   ```bash
   aws configure
   # Enter your access key and secret key again
   ```

#### VPC and Networking Issues

**Error**: `Error creating VPC: VpcLimitExceeded`

**Solution**:
```bash
# List existing VPCs
aws ec2 describe-vpcs --query 'Vpcs[*].[VpcId,Tags[?Key==`Name`].Value|[0],State]' --output table

# Delete unused VPCs
aws ec2 delete-vpc --vpc-id vpc-xxxxx

# Or request limit increase via AWS Support
```

**Error**: Lambda can't connect to RDS

**Symptoms**:
- API returns 500 errors
- Lambda logs show: `could not connect to server: Connection timed out`

**Solutions**:
1. **Check Lambda is in VPC**:
   ```bash
   aws lambda get-function-configuration --function-name salesai-dev-api \
     --query 'VpcConfig'
   ```

2. **Verify NAT Gateway exists and is available**:
   ```bash
   aws ec2 describe-nat-gateways \
     --filter "Name=state,Values=available"
   ```

3. **Check security groups**:
   ```bash
   # Lambda security group should allow outbound to RDS port 5432
   aws ec2 describe-security-groups \
     --filters "Name=tag:Name,Values=salesai-dev-lambda-sg"
   
   # RDS security group should allow inbound from Lambda SG
   aws ec2 describe-security-groups \
     --filters "Name=tag:Name,Values=salesai-dev-rds-sg"
   ```

4. **Test RDS connectivity from Lambda**:
   - Create test Lambda function in same VPC
   - Try connecting to RDS endpoint
   - Check CloudWatch logs

#### RDS Database Issues

**Error**: `database "salesai_db" does not exist`

**Solution**:
```bash
# Connect to RDS
psql -h your-rds-endpoint.rds.amazonaws.com -U salesai_admin -d postgres

# Create database
CREATE DATABASE salesai_db;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE salesai_db TO salesai_admin;

# Exit and reconnect to new database
\q
psql -h your-rds-endpoint.rds.amazonaws.com -U salesai_admin -d salesai_db

# Run migrations
alembic upgrade head
```

**Error**: `password authentication failed for user`

**Solutions**:
1. **Verify password in Secrets Manager**:
   ```bash
   aws secretsmanager get-secret-value \
     --secret-id salesai-dev-db-password \
     --query SecretString --output text
   ```

2. **Reset RDS password**:
   ```bash
   aws rds modify-db-instance \
     --db-instance-identifier salesai-dev-db \
     --master-user-password 'NewStrongPassword123!'
   ```

3. **Update secret in Secrets Manager**:
   ```bash
   aws secretsmanager update-secret \
     --secret-id salesai-dev-db-password \
     --secret-string 'NewStrongPassword123!'
   ```

4. **Restart Lambda to pick up new password**:
   ```bash
   aws lambda update-function-configuration \
     --function-name salesai-dev-api \
     --environment "Variables={FORCE_RELOAD=true}"
   ```

### Lambda Function Issues

#### Cold Start Performance

**Symptom**: First request takes 5-10 seconds, subsequent requests are fast

**Solutions**:

1. **Increase Lambda memory** (also increases CPU):
   ```bash
   aws lambda update-function-configuration \
     --function-name salesai-dev-api \
     --memory-size 1024
   # Costs more but significantly faster
   ```

2. **Enable Lambda SnapStart** (Python 3.11+):
   - Reduces cold start time by up to 10x
   - Additional cost per invocation

3. **Use Provisioned Concurrency** (expensive):
   ```bash
   aws lambda put-provisioned-concurrency-config \
     --function-name salesai-dev-api \
     --provisioned-concurrent-executions 1
   # Keeps 1 instance always warm
   ```

4. **Optimize cold start**:
   - Minimize package size
   - Lazy load heavy imports
   - Use Lambda Layers for dependencies

#### Lambda Timeout Errors

**Error**: `Task timed out after 30.00 seconds`

**Solutions**:

1. **Increase timeout**:
   ```bash
   aws lambda update-function-configuration \
     --function-name salesai-dev-api \
     --timeout 60
   # Max: 900 seconds (15 minutes)
   ```

2. **Optimize slow queries**:
   - Add database indexes
   - Use query pagination
   - Cache frequently accessed data

3. **Check what's slow**:
   - Review CloudWatch logs
   - Add timing logs:
   ```python
   import time
   start = time.time()
   # ... operation ...
   print(f"Operation took {time.time() - start}s")
   ```

#### Lambda Out of Memory

**Error**: `Runtime.OutOfMemory`

**Solutions**:

1. **Increase memory**:
   ```bash
   aws lambda update-function-configuration \
     --function-name salesai-dev-api \
     --memory-size 2048
   ```

2. **Optimize memory usage**:
   - Don't load large files into memory
   - Stream large responses
   - Close database connections
   - Clear large variables after use

#### Environment Variables Not Loading

**Symptom**: Lambda can't read secrets or config

**Solutions**:

1. **Check Lambda environment variables**:
   ```bash
   aws lambda get-function-configuration \
     --function-name salesai-dev-api \
     --query 'Environment'
   ```

2. **Verify Secrets Manager access**:
   ```bash
   # Check Lambda execution role has secretsmanager:GetSecretValue permission
   aws lambda get-function-configuration \
     --function-name salesai-dev-api \
     --query 'Role'
   ```

3. **Update environment variables**:
   ```bash
   aws lambda update-function-configuration \
     --function-name salesai-dev-api \
     --environment "Variables={
       OPENAI_API_KEY=sk-...,
       TELEGRAM_BOT_TOKEN=...,
       CLERK_SECRET_KEY=...
     }"
   ```

### API Gateway Issues

#### 403 Forbidden Errors

**Error**: API Gateway returns 403 when calling endpoints

**Solutions**:

1. **Check API Gateway resource policy**:
   ```bash
   aws apigatewayv2 get-api \
     --api-id your-api-id
   ```

2. **Verify Lambda permissions**:
   ```bash
   aws lambda get-policy \
     --function-name salesai-dev-api
   # Should show apigateway.amazonaws.com can invoke
   ```

3. **Check CORS configuration**:
   - Add your domain to allowed origins
   - Enable credentials if needed

#### 502 Bad Gateway Errors

**Error**: API Gateway returns 502

**Causes**:
- Lambda function errors/crashes
- Lambda timeout
- Invalid response format

**Solutions**:

1. **Check Lambda logs**:
   ```bash
   aws logs tail /aws/lambda/salesai-dev-api --follow
   ```

2. **Verify Lambda response format**:
   ```python
   # Lambda must return this format:
   {
       "statusCode": 200,
       "headers": {"Content-Type": "application/json"},
       "body": json.dumps({"data": "..."})
   }
   ```

3. **Test Lambda directly**:
   ```bash
   aws lambda invoke \
     --function-name salesai-dev-api \
     --payload '{"rawPath":"/api/health"}' \
     response.json
   cat response.json
   ```

### Clerk Authentication Issues

#### Users Can't Sign Up

**Symptoms**:
- Sign up button doesn't work
- No error message shown
- Stuck on loading

**Solutions**:

1. **Check Clerk publishable key**:
   ```javascript
   // frontend/.env
   VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
   // Must start with pk_test_ or pk_live_
   ```

2. **Verify allowed origins in Clerk dashboard**:
   - Go to Clerk dashboard → Settings → Domains
   - Add your CloudFront URL
   - Add `http://localhost:5173` for local dev

3. **Check browser console** (F12):
   - Look for Clerk error messages
   - Check network tab for failed requests

4. **Verify Clerk application is active**:
   - Clerk dashboard → check application status

#### Authentication Fails in Backend

**Error**: `Invalid token` or `Unauthorized` when calling API

**Solutions**:

1. **Verify Clerk secret key**:
   ```bash
   # Check Lambda environment
   aws lambda get-function-configuration \
     --function-name salesai-dev-api \
     --query 'Environment.Variables.CLERK_SECRET_KEY'
   ```

2. **Check token format**:
   - Should be: `Bearer <jwt_token>`
   - Check `Authorization` header in request

3. **Verify Clerk domain matches**:
   ```python
   # backend/.env
   CLERK_DOMAIN=your-app.clerk.accounts.dev
   # Must match exactly
   ```

4. **Test token validation**:
   ```python
   # In backend
   from clerk_backend_api import Clerk
   clerk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))
   try:
       user = clerk.users.get("user_xxx")
       print("Valid!")
   except Exception as e:
       print(f"Error: {e}")
   ```

### Telegram Bot Issues

#### Webhook Not Receiving Messages

**Symptoms**:
- Bot doesn't respond to messages
- No errors shown
- Messages sent but ignored

**Solutions**:

1. **Check webhook status**:
   ```bash
   curl "https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo"
   ```

2. **Look for errors in response**:
   ```json
   {
     "last_error_message": "Wrong response from the webhook: 500",
     "last_error_date": 1234567890
   }
   ```

3. **Verify webhook URL is accessible**:
   ```bash
   curl -X POST https://your-api-gateway-url.amazonaws.com/telegram/webhook \
     -H "Content-Type: application/json" \
     -d '{"message":{"text":"test"}}'
   ```

4. **Check Lambda logs for webhook requests**:
   ```bash
   aws logs tail /aws/lambda/salesai-dev-api --follow --filter-pattern "telegram"
   ```

5. **Re-set webhook**:
   ```bash
   # Delete webhook
   curl -X POST "https://api.telegram.org/botYOUR_TOKEN/deleteWebhook"
   
   # Set webhook again
   curl -X POST "https://api.telegram.org/botYOUR_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "YOUR_WEBHOOK_URL"}'
   ```

#### Bot Sends Messages But User Doesn't Receive

**Symptoms**:
- API logs show messages sent successfully
- User doesn't see messages in Telegram

**Solutions**:

1. **Check bot token is correct**:
   ```bash
   curl "https://api.telegram.org/botYOUR_TOKEN/getMe"
   # Should return bot info
   ```

2. **Verify chat_id is correct**:
   - Log the chat_id from incoming messages
   - Ensure you're sending to the correct chat_id

3. **Check for Telegram API errors**:
   ```python
   # Add error handling in bot code
   try:
       bot.send_message(chat_id, text)
   except Exception as e:
       logger.error(f"Telegram error: {e}")
   ```

#### AI Agent Gives Wrong Responses

**Symptoms**:
- Bot doesn't show products correctly
- Prices are wrong
- Discounts not calculated

**Solutions**:

1. **Check OpenAI API key**:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_OPENAI_KEY"
   ```

2. **Verify products exist in database**:
   ```sql
   SELECT * FROM products WHERE is_active = true;
   ```

3. **Check discount rules**:
   ```sql
   SELECT * FROM discounts WHERE is_active = true;
   ```

4. **Review AI agent prompts**:
   - Check `backend/app/services/ai_agent.py`
   - Verify system prompt is correct
   - Ensure function calling is configured

5. **Check OpenAI API usage and limits**:
   - Visit [platform.openai.com/usage](https://platform.openai.com/usage)
   - Verify you haven't hit rate limits
   - Check billing status

### Frontend Issues

#### Frontend Not Loading (Blank Page)

**Symptoms**:
- CloudFront URL shows blank page
- No error message
- Spinner loads forever

**Solutions**:

1. **Check browser console** (F12):
   - Look for JavaScript errors
   - Check network tab for failed requests

2. **Verify files uploaded to S3**:
   ```bash
   aws s3 ls s3://your-frontend-bucket/ --recursive
   # Should show index.html, assets/, etc.
   ```

3. **Check CloudFront distribution**:
   ```bash
   aws cloudfront get-distribution --id E1234567890
   # Status should be "Deployed"
   ```

4. **Invalidate CloudFront cache**:
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id E1234567890 \
     --paths "/*"
   ```

5. **Check index.html exists**:
   ```bash
   curl https://your-cloudfront-domain.cloudfront.net/index.html
   ```

#### API Calls Failing (CORS Errors)

**Error**: `Access to fetch at '...' has been blocked by CORS policy`

**Solutions**:

1. **Check CORS configuration in backend**:
   ```python
   # backend/app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://your-cloudfront-domain.cloudfront.net",
           "http://localhost:5173"
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Verify API_URL in frontend .env**:
   ```bash
   # Should match your API Gateway URL
   VITE_API_URL=https://your-api-gateway-url.amazonaws.com/api
   ```

3. **Redeploy backend after CORS changes**

4. **Check API Gateway CORS settings**:
   - Go to API Gateway console
   - Check CORS configuration
   - Ensure OPTIONS method exists

#### Build Failures

**Error**: `Module not found` or `Cannot find module`

**Solutions**:

1. **Clear npm cache**:
   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check Node version**:
   ```bash
   node --version
   # Should be 18.x or higher
   ```

3. **Install missing dependencies**:
   ```bash
   npm install
   ```

4. **Check for TypeScript errors**:
   ```bash
   npm run type-check
   ```

### Database Issues

#### Connection Pool Exhausted

**Error**: `ConnectionPool limit reached`

**Solutions**:

1. **Increase RDS max_connections**:
   ```bash
   aws rds modify-db-instance \
     --db-instance-identifier salesai-dev-db \
     --max-allocated-storage 100
   ```

2. **Optimize connection pooling in SQLAlchemy**:
   ```python
   # backend/app/database.py
   engine = create_engine(
       DATABASE_URL,
       pool_size=10,  # Increase if needed
       max_overflow=20,
       pool_pre_ping=True,
       pool_recycle=3600
   )
   ```

3. **Close connections properly**:
   ```python
   # Always use context managers
   with get_db() as db:
       # ... operations ...
       pass
   # Connection automatically closed
   ```

#### Slow Queries

**Symptom**: API responses take > 2 seconds

**Solutions**:

1. **Add database indexes**:
   ```sql
   -- Add index on frequently queried columns
   CREATE INDEX idx_products_name ON products(name);
   CREATE INDEX idx_orders_user_id ON orders(user_id);
   CREATE INDEX idx_orders_created_at ON orders(created_at);
   ```

2. **Enable query logging**:
   ```python
   # backend/app/database.py
   engine = create_engine(DATABASE_URL, echo=True)
   # This logs all SQL queries
   ```

3. **Use SELECT specific columns** instead of SELECT *:
   ```python
   # Instead of:
   db.query(Product).all()
   
   # Use:
   db.query(Product.id, Product.name, Product.price).all()
   ```

4. **Add pagination**:
   ```python
   # Add limit and offset
   products = db.query(Product).limit(50).offset(0).all()
   ```

### Deployment Issues

#### GitHub Actions Workflow Fails

**Error**: Various errors in GitHub Actions

**Solutions**:

1. **Check GitHub secrets are set** (step 11.2)

2. **View detailed logs**:
   - Click on failed step
   - Read error message
   - Check previous steps for context

3. **Re-run workflow**:
   - Click "Re-run failed jobs"
   - Sometimes transient errors (network, etc.)

4. **Test locally before pushing**:
   ```bash
   # Test build locally
   cd backend && python -m pytest
   cd ../frontend && npm run build
   ```

#### Terraform State Locked

**Error**: `Error acquiring the state lock`

**Solution**:
```bash
# Force unlock (use carefully!)
terraform force-unlock LOCK_ID

# LOCK_ID is shown in error message
```

### General Debugging Tips

#### Enable Debug Logging

**Backend**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend**:
```javascript
console.debug('Debug info:', data);
```

#### Check CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/salesai-dev-api --follow

# Search logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/salesai-dev-api \
  --filter-pattern "ERROR"
```

#### Monitor AWS Resources

```bash
# Check Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=salesai-dev-api \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

#### Get Help

If stuck:
1. Check CloudWatch logs first
2. Search GitHub issues
3. Check AWS service health dashboard
4. Review recent changes in git history
5. Ask in project discussions or open an issue

## Production Deployment Checklist

Before deploying to production, complete this comprehensive checklist:

### Pre-Deployment

#### 1. Code Review & Testing

- [ ] All features tested in development
- [ ] Unit tests passing (`pytest tests/`)
- [ ] Integration tests passing
- [ ] Frontend builds without errors (`npm run build`)
- [ ] TypeScript type checking passes (`npm run type-check`)
- [ ] Linter passes with no errors (`npm run lint`)
- [ ] Code reviewed by team member
- [ ] No console.log or debug statements in production code
- [ ] Error handling implemented for all API calls
- [ ] Loading states implemented for all async operations

#### 2. Environment Configuration

- [ ] Create production `.env` file (separate from dev)
- [ ] Update `environment` variable to "production" in Terraform
- [ ] Use production API keys (not test keys):
  - [ ] Clerk: Switch from `pk_test_` to `pk_live_`
  - [ ] Clerk: Switch from `sk_test_` to `sk_live_`
  - [ ] OpenAI: Use production key with appropriate limits
- [ ] Strong database password (20+ characters)
- [ ] Generate new encryption keys/secrets (don't reuse dev keys)
- [ ] Configure production CORS origins
- [ ] Update Telegram webhook to production URL

#### 3. AWS Infrastructure

- [ ] Use production AWS account (separate from dev if possible)
- [ ] Configure resource tags for cost tracking
- [ ] Set up proper VPC and subnets
- [ ] Configure RDS with:
  - [ ] Multi-AZ enabled (for high availability)
  - [ ] Automated backups enabled (7-30 days retention)
  - [ ] Encryption at rest enabled
  - [ ] SSL/TLS required for connections
  - [ ] Production-sized instance (db.t3.small or larger)
- [ ] Configure Lambda with:
  - [ ] Appropriate memory (1024MB+ for production)
  - [ ] Timeout: 30-60 seconds
  - [ ] Reserved concurrency (if needed)
  - [ ] Dead letter queue for failed invocations
- [ ] S3 buckets:
  - [ ] Versioning enabled
  - [ ] Encryption enabled
  - [ ] Block public access configured correctly
  - [ ] Lifecycle policies configured
- [ ] CloudFront:
  - [ ] Custom domain configured (not *.cloudfront.net)
  - [ ] SSL certificate configured (AWS Certificate Manager)
  - [ ] Caching optimized
  - [ ] Compression enabled

#### 4. Security Hardening

- [ ] Enable AWS GuardDuty for threat detection
- [ ] Enable AWS Config for compliance monitoring
- [ ] Configure AWS WAF rules (if using)
- [ ] Set up VPC Flow Logs
- [ ] Review all security groups (principle of least privilege)
- [ ] Enable MFA for AWS root account
- [ ] Enable MFA for all IAM users
- [ ] Rotate all access keys
- [ ] Remove default VPC and security groups
- [ ] Enable CloudTrail for audit logging
- [ ] Configure AWS Secrets Manager rotation
- [ ] Review IAM policies and remove unnecessary permissions
- [ ] Enable 2FA in Clerk for admin users
- [ ] Configure rate limiting on API endpoints
- [ ] Add input validation on all user inputs
- [ ] Implement CSRF protection
- [ ] Enable secure headers (CSP, HSTS, X-Frame-Options)

#### 5. Monitoring & Alerting

- [ ] Set up CloudWatch dashboards
- [ ] Configure CloudWatch alarms:
  - [ ] Lambda errors > threshold
  - [ ] Lambda duration > threshold
  - [ ] API Gateway 5xx errors
  - [ ] RDS CPU utilization > 80%
  - [ ] RDS storage space < 10%
  - [ ] RDS connection count > threshold
- [ ] Set up cost alerts
- [ ] Configure log aggregation
- [ ] Set log retention policies
- [ ] Set up on-call rotation (if 24/7 support)
- [ ] Create runbook for common issues
- [ ] Test alert notifications

#### 6. Backup & Disaster Recovery

- [ ] Verify RDS automated backups are enabled
- [ ] Test database restore from backup
- [ ] Configure RDS snapshot schedule
- [ ] Enable S3 versioning for critical buckets
- [ ] Document backup restoration procedure
- [ ] Set up cross-region backup (optional, for critical data)
- [ ] Create disaster recovery plan
- [ ] Document RTO (Recovery Time Objective) and RPO (Recovery Point Objective)

#### 7. Performance Optimization

- [ ] Database indexes created for common queries
- [ ] Lambda cold start optimized (package size < 20MB)
- [ ] CloudFront caching configured
- [ ] Frontend assets minified and compressed
- [ ] Image optimization implemented
- [ ] API response caching (if applicable)
- [ ] Database connection pooling configured
- [ ] Load testing completed
- [ ] Stress testing completed
- [ ] Identify and fix N+1 query problems

#### 8. Domain & SSL

- [ ] Purchase domain name
- [ ] Configure DNS records:
  - [ ] A record for frontend → CloudFront
  - [ ] CNAME for API → API Gateway
- [ ] Request SSL certificate via AWS Certificate Manager
- [ ] Validate certificate (DNS or email validation)
- [ ] Configure CloudFront to use custom domain
- [ ] Configure API Gateway custom domain
- [ ] Test HTTPS access
- [ ] Enforce HTTPS (redirect HTTP to HTTPS)
- [ ] Configure HSTS headers

#### 9. Clerk Production Setup

- [ ] Switch to production Clerk application (or upgrade dev app)
- [ ] Update allowed origins to production domain
- [ ] Configure production email templates
- [ ] Set up custom email sender (optional)
- [ ] Test sign-up flow in production
- [ ] Test password reset flow
- [ ] Test social logins (if enabled)
- [ ] Configure webhook endpoints (if using Clerk webhooks)
- [ ] Review and adjust rate limits
- [ ] Set up user provisioning workflow

#### 10. Documentation

- [ ] Update README with production URLs
- [ ] Document deployment procedure
- [ ] Document rollback procedure
- [ ] Create operations manual
- [ ] Document API endpoints
- [ ] Create user guide for dashboard
- [ ] Document Telegram bot commands
- [ ] Create troubleshooting guide
- [ ] Document monitoring and alerting
- [ ] Create incident response playbook

### Deployment

#### 11. Initial Deployment

1. [ ] Deploy infrastructure with Terraform:
   ```bash
   cd terraform
   terraform init
   terraform plan -var="environment=production"
   terraform apply -var="environment=production"
   ```

2. [ ] Verify all resources created successfully

3. [ ] Run database migrations:
   ```bash
   cd backend
   export DATABASE_URL="production-db-url"
   alembic upgrade head
   ```

4. [ ] Deploy backend via GitHub Actions or manually:
   ```bash
   cd backend
   ./deploy-production.sh
   ```

5. [ ] Deploy frontend via GitHub Actions or manually:
   ```bash
   cd frontend
   npm run build
   aws s3 sync dist/ s3://production-bucket/
   aws cloudfront create-invalidation --distribution-id XXX --paths "/*"
   ```

6. [ ] Configure Telegram webhook to production URL

7. [ ] Test all critical user flows

8. [ ] Verify monitoring and alerts are working

#### 12. Post-Deployment Verification

- [ ] Frontend loads correctly on production domain
- [ ] Users can sign up and sign in
- [ ] Users can add/edit/delete products
- [ ] Discounts calculate correctly
- [ ] Telegram bot responds to messages
- [ ] AI agent provides correct product information
- [ ] Orders are created successfully
- [ ] Images upload and display correctly
- [ ] All API endpoints respond correctly
- [ ] Logs appear in CloudWatch
- [ ] Metrics appear in CloudWatch dashboard
- [ ] Alerts are triggering correctly (test with simulated issues)

### Post-Deployment

#### 13. Monitoring & Maintenance

- [ ] Monitor application for first 24 hours closely
- [ ] Review CloudWatch logs daily for first week
- [ ] Review cost reports weekly
- [ ] Set up weekly automated reports
- [ ] Schedule monthly security reviews
- [ ] Schedule quarterly disaster recovery drills
- [ ] Plan capacity increases based on usage
- [ ] Monitor OpenAI API costs and usage

#### 14. Ongoing Tasks

- [ ] Rotate credentials every 90 days
- [ ] Update dependencies monthly
- [ ] Review and update documentation
- [ ] Backup and test restore procedures quarterly
- [ ] Review and optimize costs monthly
- [ ] Update security patches within 7 days of release
- [ ] Review access logs for suspicious activity
- [ ] Test disaster recovery plan quarterly
- [ ] Update SSL certificates before expiration
- [ ] Review and update monitoring alerts as needed

### Rollback Plan

In case of critical issues after deployment:

1. **Immediate Actions**:
   ```bash
   # Rollback frontend to previous version
   aws s3 sync s3://backup-bucket/ s3://production-bucket/
   aws cloudfront create-invalidation --distribution-id XXX --paths "/*"
   
   # Rollback Lambda to previous version
   aws lambda update-function-code \
     --function-name salesai-prod-api \
     --s3-bucket deployments-bucket \
     --s3-key lambda-package-previous.zip
   
   # Rollback database (if schema changed)
   cd backend
   alembic downgrade -1
   ```

2. **Communication**:
   - [ ] Notify users of the issue
   - [ ] Post status updates
   - [ ] Inform stakeholders

3. **Investigation**:
   - [ ] Analyze logs to identify root cause
   - [ ] Document the issue
   - [ ] Create fix in development
   - [ ] Test thoroughly before redeploying

### Production URLs to Update

After deployment, update these in your documentation:

- **Frontend**: `https://yourdomain.com`
- **API**: `https://api.yourdomain.com`
- **Telegram Bot**: `@YourBotUsername`
- **Admin Email**: `admin@yourdomain.com`

### Go-Live Checklist

Final checks before making app publicly available:

- [ ] All production checklist items completed
- [ ] Load testing completed with satisfactory results
- [ ] Security scan completed with no critical issues
- [ ] Legal review completed (terms of service, privacy policy)
- [ ] Support channels established
- [ ] Marketing materials prepared
- [ ] User onboarding flow tested
- [ ] Analytics and tracking configured
- [ ] Backup support team trained
- [ ] Emergency contact list created

✅ **Once all items are checked, you're ready for production!**

## Future Enhancements

### Phase 1: Core Improvements

- [ ] Multi-language support (i18n)
- [ ] Email notifications for orders
- [ ] SMS notifications (Twilio)
- [ ] Customer order history page
- [ ] Product categories and filtering
- [ ] Search functionality
- [ ] Product reviews and ratings
- [ ] Inventory alerts (low stock warnings)

### Phase 2: Payment Integration

- [ ] Stripe payment gateway
- [ ] PayPal integration
- [ ] Multiple payment methods
- [ ] Invoicing and receipts
- [ ] Refund processing
- [ ] Subscription products

### Phase 3: Advanced Features

- [ ] WhatsApp Business API integration
- [ ] Analytics dashboard with charts
- [ ] Sales reports and insights
- [ ] Advanced reporting (CSV export)
- [ ] Multi-seller/multi-store support
- [ ] Inventory management system
- [ ] Supplier management
- [ ] Purchase orders

### Phase 4: Scale & Performance

- [ ] Redis caching layer
- [ ] CDN for images
- [ ] Background job queue (Celery/Redis)
- [ ] Read replicas for database
- [ ] Auto-scaling configuration
- [ ] Performance monitoring (New Relic, Datadog)
- [ ] Load balancer with multiple Lambda instances

### Phase 5: Mobile & Extensions

- [ ] Mobile app (React Native)
- [ ] Progressive Web App (PWA)
- [ ] Browser extension for quick product add
- [ ] Desktop app (Electron)
- [ ] Shopify/WooCommerce integration
- [ ] API for third-party integrations

### Phase 6: AI Enhancements

- [ ] Product recommendations
- [ ] Automated product descriptions
- [ ] Image recognition for product matching
- [ ] Sentiment analysis on customer messages
- [ ] Chatbot training on custom data
- [ ] Voice support (speech-to-text)
- [ ] Multilingual AI agent

### Phase 7: Enterprise Features

- [ ] SSO (Single Sign-On) support
- [ ] RBAC (Role-Based Access Control)
- [ ] Audit logging
- [ ] Compliance features (GDPR, CCPA)
- [ ] White-label solution
- [ ] Multi-tenancy
- [ ] Advanced permissions system
- [ ] API rate limiting per customer

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Email: support@salesai.example.com

## Acknowledgments

- OpenAI for GPT-4 API
- Telegram for Bot API
- AWS for infrastructure
- FastAPI and React communities
