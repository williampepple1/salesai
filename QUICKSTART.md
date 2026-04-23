# Quick Start Guide

Get your AI Sales Helper running in production in under 30 minutes.

## 🚀 Fast Track Deployment

### 1️⃣ Prerequisites (5 minutes)

- [ ] AWS Account ([aws.amazon.com](https://aws.amazon.com))
- [ ] GitHub Account
- [ ] Clerk Account ([clerk.com](https://clerk.com)) - Free tier
- [ ] OpenAI API Key ([platform.openai.com](https://platform.openai.com))
- [ ] Telegram Bot Token (via @BotFather on Telegram)

### 2️⃣ Set Up Clerk (5 minutes)

1. Sign up at [clerk.com](https://clerk.com)
2. Create new application
3. Copy your keys:
   - Publishable Key: `pk_test_...`
   - Secret Key: `sk_test_...`
   - Domain: `your-app.clerk.accounts.dev`

### 3️⃣ Configure Repository (5 minutes)

**Add GitHub Secrets** (Settings → Secrets → Actions):

```
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
DB_PASSWORD=SecurePassword123!
OPENAI_API_KEY=sk-proj-your-openai-key
TELEGRAM_BOT_TOKEN=1234567890:ABCdef
CLERK_DOMAIN=your-app.clerk.accounts.dev
CLERK_SECRET_KEY=sk_test_your-key
CLERK_PUBLISHABLE_KEY=pk_test_your-key
```

**Update Terraform Variables**:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

### 4️⃣ Deploy Everything (15 minutes)

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

**Watch deployment in GitHub Actions** (Actions tab)

The workflow will:
1. ✅ Create AWS infrastructure (10-15 min)
2. ✅ Deploy backend API (2-5 min)
3. ✅ Deploy frontend dashboard (2-3 min)
4. ✅ Run health checks

### 5️⃣ Post-Deployment Setup (5 minutes)

**After deployment completes:**

1. **Get URLs from GitHub Actions summary**:
   - Frontend: `https://xxxx.cloudfront.net`
   - API: `https://xxxx.execute-api.us-east-1.amazonaws.com`

2. **Update GitHub Secrets** with URLs:
   ```
   API_URL=https://your-api-url
   S3_FRONTEND_BUCKET=salesai-frontend-123456
   CLOUDFRONT_DISTRIBUTION_ID=E1234567890
   CLOUDFRONT_DOMAIN=xxxx.cloudfront.net
   ```

3. **Configure Telegram Bot**:
   - Open your dashboard
   - Sign in with Clerk
   - Go to Settings
   - Enter bot token
   - Save

### 6️⃣ Test (5 minutes)

**Dashboard:**
- ✅ Add a product with images
- ✅ Create discount rule
- ✅ Check products page

**Telegram Bot:**
- ✅ Message your bot on Telegram
- ✅ Send `/start`
- ✅ Ask about products
- ✅ Test placing an order

## 🎉 You're Live!

Your AI Sales Helper is now running and ready to handle customer conversations 24/7!

## Next Steps

- [ ] Add all your products
- [ ] Configure discount strategies
- [ ] Test various customer scenarios
- [ ] Share bot link with customers
- [ ] Monitor orders in dashboard

## Common Issues

### "Deployment failed at infrastructure step"

**Check**:
- AWS credentials are correct
- All GitHub secrets are set
- AWS region has capacity

**Fix**: Re-run the workflow

### "Can't sign in to dashboard"

**Check**:
- Clerk configuration is correct
- `VITE_CLERK_PUBLISHABLE_KEY` is set
- Frontend deployed successfully

**Fix**: Check browser console for errors

### "Telegram bot not responding"

**Check**:
- Bot token is correct in settings
- Webhook is configured
- Lambda function is running

**Fix**: Check CloudWatch logs for errors

## Getting Help

- **Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Workflows**: [.github/workflows/README.md](.github/workflows/README.md)
- **Clerk Setup**: [CLERK_SETUP.md](CLERK_SETUP.md)
- **AI Agent**: [AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md)

## Resources

- **Main Documentation**: [README.md](README.md)
- **Manual Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Total Setup Time**: ~30 minutes
**Cost**: ~$55-60/month for AWS infrastructure
**Scalability**: Serverless, auto-scales with usage

Need help? Open an issue on GitHub!
