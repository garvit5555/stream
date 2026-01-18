# Database Migration Guide

## Overview

After deploying the authentication update, you need to run a one-time migration to add `user_id` columns to your existing database tables.

## Migration Endpoint

A migration endpoint has been added: `POST /api/migrate`

This endpoint:
- ✅ Is **safe to call multiple times** (idempotent)
- ✅ Checks if columns exist before adding them
- ✅ Returns detailed status of each step
- ✅ Can be secured with a secret key (optional)

## How to Run Migration

### Option 1: Using curl (Recommended)

```bash
curl -X POST https://your-backend-url.onrender.com/api/migrate \
  -H "Content-Type: application/json"
```

### Option 2: Using Postman or Browser Extension

1. Method: `POST`
2. URL: `https://your-backend-url.onrender.com/api/migrate`
3. Headers: `Content-Type: application/json`
4. Click "Send"

### Option 3: Using Browser Console (JavaScript)

Open browser console on any page and run:
```javascript
fetch('https://your-backend-url.onrender.com/api/migrate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' }
})
.then(r => r.json())
.then(data => console.log(data));
```

## Expected Response

**Success:**
```json
{
  "success": true,
  "steps": [
    "Users table created/verified",
    "Added user_id column to overlays table",
    "Added user_id column to stream_settings table",
    "Cleaned up 0 orphaned stream_settings",
    "Made user_id NOT NULL and UNIQUE in stream_settings",
    "Cleaned up 0 orphaned overlays",
    "Made user_id NOT NULL in overlays"
  ],
  "errors": []
}
```

**If columns already exist:**
```json
{
  "success": true,
  "steps": [
    "Users table created/verified",
    "overlays table already has user_id column",
    "stream_settings table already has user_id column"
  ],
  "errors": []
}
```

## Optional: Add Security

If you want to secure the migration endpoint, add an environment variable in Render:

1. Go to Render → Your Web Service → Environment
2. Add: `MIGRATION_SECRET=your-secret-key-here`
3. Then call the endpoint with the secret:

```bash
curl -X POST https://your-backend-url.onrender.com/api/migrate \
  -H "Content-Type: application/json" \
  -H "X-Migration-Secret: your-secret-key-here"
```

Or in the request body:
```json
{
  "secret": "your-secret-key-here"
}
```

## When to Run

1. **After deploying the updated backend** to Render
2. **Before users start using the app** (to avoid errors)
3. **Only once** (but safe to call multiple times)

## Troubleshooting

### Error: "Invalid migration secret"
- You set `MIGRATION_SECRET` but didn't provide it in the request
- Either remove the env variable or include the secret in your request

### Error: "column already exists"
- This is normal if you run it multiple times
- The endpoint handles this gracefully

### Migration fails
- Check the `errors` array in the response
- Verify your database connection
- Check Render logs for detailed error messages

## After Migration

1. ✅ Migration completed successfully
2. ✅ Register a test user account
3. ✅ Test creating overlays and stream settings
4. ✅ Verify each user has isolated data

## Important Notes

- **Existing data**: Any overlays or stream_settings without `user_id` will be deleted
- **Fresh start**: If you have important data, back it up first
- **One-time operation**: After migration, you can disable the endpoint if desired
