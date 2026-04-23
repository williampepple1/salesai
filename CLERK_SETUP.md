# Clerk Authentication Setup Guide

This guide walks you through setting up Clerk authentication for the AI Sales Helper platform.

## Why Clerk?

Clerk provides:
- **Production-ready authentication** out of the box
- **Multiple sign-in methods** (email, social providers, phone)
- **User management dashboard** for managing your users
- **Built-in security** (2FA, session management, device tracking)
- **Email verification** and password reset flows
- **No password storage** on your backend
- **Beautiful, customizable UI components**

## Step 1: Create a Clerk Account

1. Go to [clerk.com](https://clerk.com)
2. Sign up for a free account
3. Create a new application
4. Choose your preferred sign-in methods (email/password recommended to start)

## Step 2: Get Your API Keys

From your Clerk dashboard:

1. Go to **API Keys** in the sidebar
2. Copy your **Publishable Key** (starts with `pk_test_` or `pk_live_`)
3. Copy your **Secret Key** (starts with `sk_test_` or `sk_live_`)
4. Note your **Frontend API URL** (e.g., `your-app.clerk.accounts.dev`)

## Step 3: Configure Backend

### Update Environment Variables

Edit `backend/.env`:

```bash
# Clerk Authentication
CLERK_DOMAIN=your-app.clerk.accounts.dev
CLERK_SECRET_KEY=sk_test_your-secret-key-here
CLERK_PUBLISHABLE_KEY=pk_test_your-publishable-key-here
CLERK_AUDIENCE=  # Optional, leave empty for default
```

### Run Database Migration

```bash
cd backend
alembic upgrade head
```

This adds the `clerk_user_id` field to the users table.

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Frontend

### Update Environment Variables

Edit `frontend/.env`:

```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your-publishable-key-here
VITE_API_URL=http://localhost:8000/api
```

### Install Dependencies

```bash
cd frontend
npm install
```

## Step 5: Customize Clerk Appearance (Optional)

In your Clerk dashboard:

1. Go to **Customization** → **Appearance**
2. Customize colors to match your brand
3. Upload your logo
4. Adjust button styles

Or use code-based customization in `App.tsx`:

```typescript
<ClerkProvider 
  publishableKey={clerkPubKey}
  appearance={{
    elements: {
      formButtonPrimary: 'bg-primary-600 hover:bg-primary-700',
      card: 'shadow-lg',
    },
    layout: {
      socialButtonsPlacement: 'bottom',
    }
  }}
>
```

## Step 6: Configure Sign-In Methods

In Clerk dashboard → **User & Authentication** → **Email, Phone, Username**:

1. **Enable Email Address** (required)
2. **Enable Username** (optional but recommended)
3. **Configure Email Verification** (recommended for production)
4. **Set up Social Connections** (Google, GitHub, etc.) if desired

## Step 7: Set Up JWT Template (For Backend Integration)

1. In Clerk dashboard → **JWT Templates**
2. Create a new template named "salesai-backend"
3. Add custom claims if needed
4. Copy the template ID
5. Update your backend `.env`:

```bash
CLERK_AUDIENCE=your-template-id  # If using custom JWT template
```

## Step 8: Test the Integration

### Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### Start Frontend

```bash
cd frontend
npm run dev
```

### Test Authentication Flow

1. Navigate to `http://localhost:5173`
2. You should see Clerk's sign-in page
3. Create a new account
4. Verify it redirects to the dashboard
5. Check that your user appears in Clerk dashboard

## Step 9: Deploy to Production

### Backend (AWS Lambda)

Update Terraform variables or Secrets Manager:

```hcl
CLERK_DOMAIN = "your-app.clerk.accounts.dev"
CLERK_SECRET_KEY = "sk_live_your-production-key"
CLERK_PUBLISHABLE_KEY = "pk_live_your-production-key"
```

### Frontend (S3/CloudFront)

Update GitHub Actions secrets:

```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_live_your-production-key
```

Build and deploy:

```bash
npm run build
aws s3 sync dist/ s3://your-bucket/
```

## Security Best Practices

### 1. Use Production Keys in Production

- Never use test keys (`pk_test_`, `sk_test_`) in production
- Rotate keys if compromised
- Store keys in AWS Secrets Manager, not in code

### 2. Configure Allowed Origins

In Clerk dashboard → **Allowed Origins**:

```
http://localhost:5173
https://your-production-domain.com
```

### 3. Enable Multi-Factor Authentication

In Clerk dashboard → **User & Authentication** → **Multi-factor**:

- Enable SMS or TOTP
- Optionally require MFA for all users

### 4. Set Up Session Management

In Clerk dashboard → **Sessions**:

- Configure session lifetime
- Enable multi-session support if needed
- Set up inactivity timeout

### 5. Configure Security Features

- **Email Verification**: Require before access
- **Password Complexity**: Set minimum requirements
- **Rate Limiting**: Prevent brute force attacks
- **Device Detection**: Track sign-ins from new devices

## User Flow

### New User Registration

1. User clicks "Sign Up" on your app
2. Clerk shows registration form
3. User enters email and password
4. Email verification sent (if enabled)
5. User verifies email
6. User redirected to dashboard
7. Backend automatically creates user record on first API call

### Existing User Login

1. User enters credentials
2. Clerk validates
3. JWT token issued
4. Frontend stores token
5. All API calls include token
6. Backend validates token with Clerk
7. User data loaded from database

### Password Reset

1. User clicks "Forgot Password"
2. Clerk sends reset email
3. User clicks link
4. Sets new password
5. Automatically signed in

## Troubleshooting

### Error: "Missing Clerk Publishable Key"

**Solution**: Add `VITE_CLERK_PUBLISHABLE_KEY` to frontend `.env`

### Error: "Invalid token"

**Possible causes**:
- Wrong secret key in backend
- Domain mismatch
- Expired token

**Solution**: 
- Verify `CLERK_DOMAIN` matches your Clerk app
- Check `CLERK_SECRET_KEY` is correct
- Ensure user is signed in

### Users not appearing in database

**Solution**: 
- User record is created on first API call
- Check backend logs for errors
- Verify database connection

### CORS errors

**Solution**:
- Add your frontend URL to Clerk's Allowed Origins
- Check backend CORS configuration
- Ensure API URL is correct

## Advanced Features

### Custom Claims

Add business-specific data to JWT:

1. Clerk dashboard → JWT Templates
2. Add custom claims:

```json
{
  "business_name": "{{user.public_metadata.business_name}}",
  "role": "{{user.public_metadata.role}}"
}
```

3. Access in backend:

```python
payload = clerk_auth.verify_token(token)
business_name = payload.get("business_name")
```

### Webhooks

Listen for user events (sign up, update, delete):

1. Clerk dashboard → Webhooks
2. Add endpoint: `https://your-api.com/webhooks/clerk`
3. Select events to monitor
4. Implement webhook handler in backend

### Organizations

Enable multi-tenant features:

1. Clerk dashboard → Organizations
2. Enable organization features
3. Update user model to include organization_id
4. Filter data by organization

## Migration from JWT Auth

If you had the old JWT-based auth:

1. Run the Clerk migration: `alembic upgrade head`
2. Users will need to re-register with Clerk
3. Or implement a migration script to:
   - Create Clerk users programmatically
   - Link existing database records
   - Send password reset emails

## Support

- **Clerk Documentation**: https://clerk.com/docs
- **Clerk Discord**: https://clerk.com/discord
- **Support**: support@clerk.com

## Cost

- **Free tier**: Up to 10,000 monthly active users
- **Pro tier**: Starts at $25/month
- **Enterprise**: Custom pricing

Perfect for getting started and scaling as you grow!
