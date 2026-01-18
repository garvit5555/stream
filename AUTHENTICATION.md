# Authentication System

This application now includes JWT-based authentication, allowing multiple users to have their own separate overlays and stream settings.

## Features

- **User Registration**: Users can create accounts with username, email, and password
- **User Login**: Secure login with JWT tokens
- **User Isolation**: Each user can only see and manage their own overlays and stream settings
- **Token-based Authentication**: JWT tokens stored in localStorage
- **Automatic Token Refresh**: Tokens expire after 7 days

## Backend Changes

### New Dependencies
- `PyJWT==2.8.0` - For JWT token generation and validation
- `werkzeug==3.0.1` - For password hashing

### New Database Models

**User Model:**
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `password_hash` - Hashed password (never stored in plain text)
- `created_at` - Account creation timestamp

**Updated Models:**
- `Overlay` - Now includes `user_id` foreign key
- `StreamSettings` - Now includes `user_id` foreign key (one per user)

### New API Endpoints

**Authentication:**
- `POST /api/auth/register` - Register a new user
  - Body: `{ "username": "...", "email": "...", "password": "..." }`
  - Returns: `{ "token": "...", "user": {...} }`

- `POST /api/auth/login` - Login user
  - Body: `{ "username": "...", "password": "..." }`
  - Returns: `{ "token": "...", "user": {...} }`

- `GET /api/auth/me` - Get current user (requires authentication)
  - Headers: `Authorization: Bearer <token>`
  - Returns: `{ "id": 1, "username": "...", "email": "..." }`

### Protected Endpoints

All overlay and stream settings endpoints now require authentication:
- All `/api/overlays/*` endpoints
- All `/api/stream/*` endpoints

**Authentication Header:**
```
Authorization: Bearer <jwt_token>
```

## Frontend Changes

### New Components
- `Login.js` - Login/Register modal component
- `Login.css` - Styling for login component

### New Services
- `auth.js` - Authentication service for managing tokens and user data

### Updated Components
- `App.js` - Now checks authentication and shows login if not authenticated
- `api.js` - Automatically adds JWT token to all API requests
- All API calls now include authentication headers

### User Flow

1. **First Visit**: User sees login/register form
2. **Registration**: User creates account → receives JWT token
3. **Login**: User logs in → receives JWT token
4. **Authenticated**: Token stored in localStorage, user can access app
5. **API Calls**: All requests automatically include JWT token
6. **Logout**: Token cleared, user redirected to login

## Environment Variables

### Backend
Add to your `.env` file:
```
SECRET_KEY=your-secret-key-here-change-in-production
```

**Important**: Use a strong, random secret key in production!

### Frontend
No new environment variables needed. Uses existing `REACT_APP_API_URL`.

## Database Migration

When you deploy this update, the database will automatically:
1. Create the `users` table
2. Add `user_id` columns to `overlays` and `stream_settings` tables
3. Existing data will need to be migrated (if any)

**Note**: If you have existing data, you'll need to:
- Create a migration script to assign existing overlays to a default user
- Or start fresh (existing data will be inaccessible without user_id)

## Security Features

1. **Password Hashing**: Passwords are hashed using Werkzeug's secure hashing
2. **JWT Tokens**: Secure token-based authentication
3. **Token Expiration**: Tokens expire after 7 days
4. **User Isolation**: Database queries filter by user_id
5. **CORS Protection**: Only allowed origins can access the API

## Testing

### Register a New User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### Access Protected Endpoint
```bash
curl -X GET http://localhost:5000/api/overlays \
  -H "Authorization: Bearer <your_token_here>"
```

## Deployment Notes

1. **Set SECRET_KEY**: Make sure to set a strong `SECRET_KEY` in your Render environment variables
2. **Database Migration**: The database will auto-create tables, but existing data needs migration
3. **Frontend**: No changes needed to Netlify deployment, just redeploy after code push

## Future Enhancements

Possible improvements:
- Password reset functionality
- Email verification
- Refresh token mechanism
- Role-based access control (admin/user)
- Social login (Google, GitHub, etc.)
