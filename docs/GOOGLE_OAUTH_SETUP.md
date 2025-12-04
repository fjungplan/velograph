# Google OAuth Setup Guide

This guide will walk you through setting up Google OAuth authentication for the Velograph application.

## Prerequisites

- A Google Account
- Access to the Google Cloud Console

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Velograph Auth")
5. Click "Create"

### 2. Enable Google+ API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Google+ API"
3. Click on it and press "Enable"
4. Also enable "Google Identity Toolkit API" (recommended)

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have a Google Workspace account)
3. Click "Create"
4. Fill in the required information:
   - **App name**: Velograph
   - **User support email**: Your email
   - **Developer contact email**: Your email
5. Click "Save and Continue"
6. On the "Scopes" page, click "Add or Remove Scopes"
7. Add these scopes:
   - `openid`
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
8. Click "Update" and then "Save and Continue"
9. Add test users if needed (during development)
10. Click "Save and Continue" and then "Back to Dashboard"

### 4. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application"
4. Enter a name (e.g., "Velograph Web Client")
5. Under "Authorized JavaScript origins", add:
   - `http://localhost:5173` (for local development)
   - Your production domain (e.g., `https://velograph.com`)
6. Under "Authorized redirect URIs", add:
   - `http://localhost:5173/auth/callback` (for local development)
   - Your production callback URL (e.g., `https://velograph.com/auth/callback`)
7. Click "Create"
8. A dialog will appear with your credentials:
   - **Client ID**: Copy this value
   - **Client Secret**: Copy this value
9. Click "OK"

### 5. Configure Backend Environment Variables

Create or update your `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://cycling:cycling@postgres:5432/cycling_lineage

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback

# JWT Secret (IMPORTANT: Generate a strong random secret for production!)
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (add your production domain here)
CORS_ORIGINS=["http://localhost:5173","http://localhost:5174","https://your-production-domain.com"]
```

### 6. Generate a Strong JWT Secret

For production, generate a strong random secret:

**Linux/macOS:**
```bash
openssl rand -hex 32
```

**Windows (PowerShell):**
```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

**Python:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

Replace `JWT_SECRET_KEY` in your `.env` file with the generated value.

### 7. Configure Frontend Environment Variables

Create or update your `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
```

**Important**: Use the same `GOOGLE_CLIENT_ID` as in the backend.

### 8. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend (will be done in Prompt 22):**
```bash
cd frontend
npm install @react-oauth/google jwt-decode
```

### 9. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

This will create the `users` and `refresh_tokens` tables.

### 10. Test the Setup

1. Start the backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Visit the API docs: http://localhost:8000/docs

3. You should see the new auth endpoints:
   - `POST /api/v1/auth/google` - Authenticate with Google
   - `POST /api/v1/auth/refresh` - Refresh access token
   - `GET /api/v1/auth/me` - Get current user info

## Security Best Practices

### For Development

- Keep your `.env` file out of version control (already in `.gitignore`)
- Use `http://localhost` for development
- Test users can be added in Google Cloud Console

### For Production

1. **Use HTTPS**: Always use HTTPS in production
2. **Strong JWT Secret**: Use a cryptographically secure random string (32+ characters)
3. **Environment Variables**: Never commit secrets to version control
4. **Rotate Secrets**: Regularly rotate your JWT secret and Google OAuth credentials
5. **CORS Configuration**: Restrict `CORS_ORIGINS` to your actual domains only
6. **Token Expiry**: Keep access tokens short-lived (15 minutes recommended)
7. **Refresh Tokens**: Store refresh tokens securely (already hashed in database)
8. **Rate Limiting**: Consider adding rate limiting to auth endpoints
9. **GDPR Compliance**: Ensure proper consent and data handling (already configured)

## Testing Authentication

### Using curl

**1. Get a Google ID token** (you'll need to implement the frontend flow or use Google's OAuth Playground)

**2. Authenticate:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/google \
  -H "Content-Type: application/json" \
  -d '{"id_token": "your-google-id-token-here"}'
```

**3. Use the access token:**
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer your-access-token-here"
```

**4. Refresh the token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token-here"}'
```

### Using the Swagger UI

1. Go to http://localhost:8000/docs
2. Click on an auth endpoint (e.g., `/api/v1/auth/me`)
3. Click "Try it out"
4. For endpoints requiring authentication, click the "Authorize" button at the top
5. Enter your token in the format: `Bearer your-token-here`

## Troubleshooting

### "Invalid Google token" Error

- Verify your `GOOGLE_CLIENT_ID` matches in both backend and frontend
- Ensure the token hasn't expired (Google ID tokens expire after 1 hour)
- Check that the Google+ API is enabled in your project
- Verify the token issuer is `accounts.google.com`

### "Account banned" Error

- Check the `users` table in your database
- If a user's `is_banned` is `TRUE`, they cannot authenticate
- Update the database to unban: `UPDATE users SET is_banned = FALSE WHERE email = 'user@example.com';`

### CORS Errors

- Ensure `CORS_ORIGINS` in backend includes your frontend URL
- Check that the frontend is making requests to the correct backend URL
- Verify the backend is running and accessible

### Token Expiry Issues

- Access tokens expire after 15 minutes (configurable in settings)
- Use the refresh token endpoint to get a new access token
- Refresh tokens expire after 7 days (configurable in settings)

## Multi-Environment Setup

### Development
```env
GOOGLE_CLIENT_ID=your-dev-client-id.apps.googleusercontent.com
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback
CORS_ORIGINS=["http://localhost:5173"]
```

### Production
```env
GOOGLE_CLIENT_ID=your-prod-client-id.apps.googleusercontent.com
GOOGLE_REDIRECT_URI=https://velograph.com/auth/callback
CORS_ORIGINS=["https://velograph.com"]
JWT_SECRET_KEY=strong-production-secret-32-chars-minimum
```

**Note**: You can use the same Google OAuth Client ID for both environments by adding both redirect URIs in the Google Cloud Console, or create separate OAuth credentials for each environment.

## Next Steps

After completing this setup, you can proceed with:
- **Prompt 22**: Frontend auth integration (Google login button, token management)
- **Prompt 23+**: User-specific features (editing, moderation, etc.)

## Support

If you encounter issues:
1. Check the backend logs for error messages
2. Verify all environment variables are set correctly
3. Ensure database migrations have run successfully
4. Review the Google Cloud Console for API errors
5. Check the [FastAPI documentation](https://fastapi.tiangolo.com/) for additional help
