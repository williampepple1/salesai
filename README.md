# AI Sales Helper

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

- AWS Account with appropriate permissions
- Node.js 18+
- Python 3.11+
- Terraform 1.6+
- **Clerk account** (free tier available)
- OpenAI API key
- Telegram bot token (from @BotFather)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/salesai.git
cd salesai
```

### 2. Configure AWS Credentials

```bash
aws configure
```

### 3. Set Up Terraform Backend (Optional but Recommended)

Create an S3 bucket for Terraform state:

```bash
aws s3 mb s3://salesai-terraform-state
```

Update `terraform/main.tf` with your bucket name.

### 4. Set Up Clerk Authentication

Before deploying, you need to set up Clerk:

1. Create a free account at [clerk.com](https://clerk.com)
2. Create a new application
3. Get your API keys from the dashboard
4. Follow the detailed setup guide: **[CLERK_SETUP.md](CLERK_SETUP.md)**

### 5. Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
project_name = "salesai"
environment  = "dev"
aws_region   = "us-east-1"

db_username = "salesai_admin"
db_password = "YOUR_SECURE_PASSWORD"

openai_api_key         = "sk-your-openai-api-key"
telegram_bot_token     = "your-telegram-bot-token"
clerk_domain           = "your-app.clerk.accounts.dev"
clerk_secret_key       = "sk_test_your-clerk-secret-key"
clerk_publishable_key  = "pk_test_your-clerk-publishable-key"
```

### 6. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Note the outputs:
- `api_gateway_url` - Your API endpoint
- `frontend_url` - CloudFront URL for the dashboard
- `telegram_webhook_url` - Webhook URL for Telegram

### 7. Set Up GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
DB_PASSWORD
OPENAI_API_KEY
TELEGRAM_BOT_TOKEN
CLERK_DOMAIN
CLERK_SECRET_KEY
CLERK_PUBLISHABLE_KEY
API_URL (your API Gateway URL)
S3_FRONTEND_BUCKET
CLOUDFRONT_DISTRIBUTION_ID
CLOUDFRONT_DOMAIN
```

### 8. Automated Deployment (Recommended)

**The project includes a unified deployment workflow that handles everything automatically in the correct order:**

```
1. Infrastructure (Terraform) → 2. Backend (Lambda) → 3. Frontend (S3) → 4. Verification
```

**To deploy everything:**

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

GitHub Actions will automatically:
- Deploy infrastructure with Terraform
- Build and deploy backend to Lambda
- Build and deploy frontend to S3
- Invalidate CloudFront cache
- Run health checks

**Or deploy via GitHub UI:**
1. Go to Actions tab
2. Select "Complete Deployment"
3. Click "Run workflow"
4. Choose which components to deploy (or deploy all)
5. Monitor progress in real-time

📖 **See [.github/workflows/README.md](.github/workflows/README.md) for detailed deployment options**

### 9. Manual Deployment (Optional)

If you prefer manual deployment:

#### Deploy Backend

The backend will be automatically deployed via GitHub Actions when you push to main, or deploy manually:

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create Lambda package
mkdir -p lambda-package
pip install -r requirements.txt -t lambda-package/
cp -r app lambda-package/
cp lambda_handler.py lambda-package/
cd lambda-package
zip -r ../lambda-package.zip .
cd ..

# Deploy with Terraform
cd ../terraform
terraform apply -target=aws_lambda_function.api
```

#### Deploy Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=https://your-api-gateway-url.amazonaws.com/api" > .env

# Build and deploy
npm run build
aws s3 sync dist/ s3://your-frontend-bucket/ --delete
```

### 10. Configure Telegram Bot

1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Log into your dashboard
5. Go to Settings
6. Paste your bot token and save
7. The webhook will be automatically configured

### 11. Test the System

1. Add products in the dashboard
2. Configure discount rules
3. Open your Telegram bot
4. Send `/start` to begin
5. Test the conversation flow

## Local Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your values

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your API URL

# Run development server
npm run dev
```

Visit `http://localhost:5173` for the dashboard.

### Running Tests

```bash
cd backend
pytest tests/ -v
```

## Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
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

## Security Considerations

- All API endpoints require JWT authentication (except Telegram webhook)
- Secrets stored in AWS Secrets Manager
- RDS in private subnet with security group restrictions
- S3 buckets with minimal public access
- CORS properly configured
- HTTPS enforced via CloudFront
- Rate limiting on API Gateway

## Cost Estimation

### AWS Resources (Monthly)

- RDS db.t3.micro: ~$15
- Lambda: ~$5 (with 100k requests)
- S3: ~$1
- CloudFront: ~$1
- NAT Gateway: ~$32
- VPC: Free
- API Gateway: ~$3.50 (per million requests)

**Estimated Total: $57-60/month**

### External Services

- OpenAI API: Pay per use (varies by conversation volume)
- Telegram: Free

## Troubleshooting

### Lambda Cold Starts

If experiencing slow first requests, consider:
- Increasing Lambda memory (improves CPU)
- Using provisioned concurrency (additional cost)
- Implementing connection pooling optimization

### Database Connection Issues

- Ensure Lambda is in VPC with NAT Gateway
- Check security groups allow Lambda → RDS on port 5432
- Verify DATABASE_URL is correct

### Telegram Webhook Not Working

- Verify webhook URL is accessible publicly
- Check API Gateway logs
- Ensure bot token is correct
- Use Telegram's webhook info: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`

## Future Enhancements

- [ ] Multi-language support
- [ ] Payment gateway integration (Stripe)
- [ ] Email notifications
- [ ] WhatsApp integration
- [ ] Analytics dashboard with charts
- [ ] Multi-seller support
- [ ] Mobile app (React Native)
- [ ] Inventory alerts
- [ ] Customer reviews
- [ ] Advanced reporting

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
