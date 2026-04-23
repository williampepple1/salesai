# Authentication Architecture

## Overview

This application uses **Clerk** for authentication and authorization. Clerk provides a complete authentication solution with user management, session handling, and security features built-in.

## Why Clerk?

### Benefits

1. **Production-Ready**: No need to implement JWT refresh tokens, password hashing, or email verification
2. **Security**: Built-in protection against common attacks (CSRF, XSS, brute force)
3. **User Management**: Dashboard for viewing and managing users
4. **Multiple Auth Methods**: Email, social logins, phone, magic links
5. **No Password Storage**: Passwords are securely managed by Clerk
6. **Session Management**: Automatic token refresh and session invalidation
7. **2FA/MFA**: Optional two-factor authentication
8. **Compliance**: SOC 2 Type II certified

### Comparison to Custom JWT

| Feature | Custom JWT | Clerk |
|---------|-----------|-------|
| Implementation Time | 2-3 days | 1 hour |
| Security Maintenance | Ongoing | Managed |
| User Dashboard | Build yourself | Included |
| Social Logins | Integrate each | Pre-integrated |
| Password Reset | Build flow | Included |
| Email Verification | Build & send | Included |
| 2FA | Implement | Toggle on |
| Session Management | Manual refresh | Automatic |
| Cost | Server time | Free tier available |

## Architecture Flow

```
┌─────────────┐
│   Browser   │
│   (React)   │
└──────┬──────┘
       │
       │ 1. Sign In
       ▼
┌─────────────┐
│   Clerk     │ 2. Returns JWT
│   Service   │    Token
└──────┬──────┘
       │
       │ 3. API Request
       │    with JWT
       ▼
┌─────────────┐
│  Backend    │ 4. Validates JWT
│  (FastAPI)  │    with Clerk
└──────┬──────┘
       │
       │ 5. Returns
       │    User Data
       ▼
┌─────────────┐
│  Database   │
│ (PostgreSQL)│
└─────────────┘
```

## Frontend Authentication

### Setup

```typescript
// App.tsx
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react';

<ClerkProvider publishableKey={process.env.VITE_CLERK_PUBLISHABLE_KEY}>
  <App />
</ClerkProvider>
```

### Protected Routes

```typescript
<SignedIn>
  <DashboardLayout />
</SignedIn>
<SignedOut>
  <RedirectToSignIn />
</SignedOut>
```

### Getting User Info

```typescript
import { useUser } from '@clerk/clerk-react';

function Profile() {
  const { user } = useUser();
  
  return <div>Welcome {user?.firstName}!</div>;
}
```

### Getting Auth Token for API Calls

```typescript
import { useAuth } from '@clerk/clerk-react';

function useApiCall() {
  const { getToken } = useAuth();
  
  const callApi = async () => {
    const token = await getToken();
    const response = await fetch('/api/data', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
  };
}
```

## Backend Authentication

### JWT Validation

```python
# clerk_auth.py
class ClerkAuth:
    def verify_token(self, token: str) -> dict:
        # Get public key from Clerk's JWKS endpoint
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        
        # Verify and decode token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.CLERK_AUDIENCE
        )
        
        return payload
```

### Protected Endpoints

```python
from fastapi import Depends
from .clerk_auth import get_current_user

@router.get("/products")
async def get_products(
    current_user: User = Depends(get_current_user)
):
    # current_user is automatically available
    return await get_user_products(current_user.id)
```

### User Creation

Users are automatically created in your database on first API call:

```python
async def get_current_user(token: str, db: Session):
    payload = clerk_auth.verify_token(token)
    clerk_user_id = payload.get("sub")
    
    # Get or create user
    user = db.query(User).filter(
        User.clerk_user_id == clerk_user_id
    ).first()
    
    if not user:
        # Create new user on first login
        user = User(
            clerk_user_id=clerk_user_id,
            email=payload.get("email"),
            username=payload.get("username")
        )
        db.add(user)
        db.commit()
    
    return user
```

## Security Features

### Token Validation

1. **Signature Verification**: Uses RS256 with Clerk's public keys
2. **Expiration Check**: Tokens expire after configured time
3. **Audience Verification**: Ensures token is for your app
4. **Issuer Verification**: Confirms token is from Clerk

### Session Management

- **Short-lived Tokens**: Access tokens expire quickly (typically 1 hour)
- **Automatic Refresh**: Clerk handles token refresh transparently
- **Multi-device**: Sessions tracked across devices
- **Session Revocation**: Can invalidate sessions from Clerk dashboard

### Protection Against Attacks

- **CSRF**: Clerk tokens are immune to CSRF
- **XSS**: Tokens stored securely in HTTP-only cookies (optional)
- **Brute Force**: Rate limiting built-in
- **Token Replay**: Each token is single-use with refresh mechanism

## User Management

### Clerk Dashboard Features

- View all users
- Search and filter
- Delete users
- Block/unblock users
- View user sessions
- See sign-in history
- Manage user metadata

### User Metadata

Store custom data with users:

```typescript
// Frontend
await user.update({
  publicMetadata: {
    businessName: "My Store"
  }
});
```

```python
# Backend - access in JWT
payload = verify_token(token)
business_name = payload.get("business_name")
```

## Multi-Factor Authentication

Enable in Clerk dashboard:

1. Go to **User & Authentication** → **Multi-factor**
2. Enable **SMS** or **TOTP authenticator apps**
3. Optionally require for all users or make optional

Users can then enable 2FA in their profile settings.

## Social Logins

Add social providers in Clerk dashboard:

1. **Google**: Configure OAuth app in Google Cloud Console
2. **GitHub**: Configure OAuth app in GitHub
3. **Microsoft**: Configure in Azure
4. **More**: Facebook, Apple, LinkedIn, etc.

Users can then sign in with one click.

## Webhooks

Listen for user events:

```python
@router.post("/webhooks/clerk")
async def clerk_webhook(request: Request):
    # Verify webhook signature
    # Handle events: user.created, user.updated, user.deleted
    pass
```

Events you can listen for:
- `user.created` - New user signed up
- `user.updated` - User profile changed
- `user.deleted` - User deleted account
- `session.created` - User signed in
- `session.ended` - User signed out

## Testing

### Local Development

```bash
# Backend
export CLERK_DOMAIN=your-app.clerk.accounts.dev
export CLERK_SECRET_KEY=sk_test_...
uvicorn app.main:app --reload

# Frontend
export VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
npm run dev
```

### Test Users

Create test users in Clerk dashboard for development.

### End-to-End Tests

```typescript
// Clerk provides test mode for E2E tests
test('protected route', async () => {
  await clerk.signIn({ 
    identifier: 'test@example.com',
    password: 'testpassword'
  });
  
  await expect(page).toContainText('Dashboard');
});
```

## Migration from JWT

If migrating from custom JWT:

1. **Run migration**: Add `clerk_user_id` column
2. **Dual authentication**: Support both temporarily
3. **Migrate users**: 
   - Email existing users
   - Users re-register with Clerk
   - Or bulk import via Clerk API
4. **Remove old auth**: Once migrated, remove JWT code

## Troubleshooting

### Common Issues

**Token Invalid**
- Check `CLERK_DOMAIN` matches your app
- Verify `CLERK_SECRET_KEY` is correct
- Ensure token not expired

**CORS Errors**
- Add frontend URL to Clerk's Allowed Origins
- Check API CORS configuration

**User Not Created**
- Check backend logs
- Verify database connection
- Ensure migration ran

**Session Expired**
- Clerk automatically refreshes
- May need to sign in again after long inactivity

## Best Practices

1. **Use Test Keys in Development**: Never use production keys locally
2. **Rotate Keys Regularly**: Especially if compromised
3. **Enable Email Verification**: Prevents fake accounts
4. **Configure Session Timeout**: Balance security and UX
5. **Monitor Clerk Dashboard**: Watch for suspicious activity
6. **Use Webhooks**: Sync user data changes
7. **Store Keys Securely**: Use AWS Secrets Manager in production

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk + FastAPI Guide](https://clerk.com/docs/backend-requests/handling/python)
- [Clerk + React Guide](https://clerk.com/docs/quickstarts/react)
- [Security Best Practices](https://clerk.com/docs/security/overview)
