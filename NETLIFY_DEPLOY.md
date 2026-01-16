# Quick Netlify Deployment Guide

## Step 1: Deploy Frontend to Netlify

### Via GitHub (Easiest):

1. **Go to Netlify**: https://app.netlify.com
   - Sign in with GitHub

2. **Import Project**:
   - Click "Add new site" → "Import an existing project"
   - Select: `garvit5555/stream`

3. **Build Settings** (Netlify will auto-detect from `netlify.toml`):
   - Base directory: (leave empty)
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/build`

4. **Environment Variables** (Set after backend is deployed):
   - Go to: Site settings → Environment variables
   - Add: `REACT_APP_API_URL` = `https://your-backend-url.onrender.com/api`

5. **Deploy**:
   - Click "Deploy site"
   - Wait 2-3 minutes
   - Your site: `https://your-site-name.netlify.app`

## Step 2: Deploy Backend to Render

1. **Go to Render**: https://render.com
   - Sign in with GitHub

2. **New Web Service**:
   - Click "New" → "Web Service"
   - Connect repo: `garvit5555/stream`

3. **Settings**:
   - Name: `livestream-backend`
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Add PostgreSQL**:
   - Click "New" → "PostgreSQL"
   - Name: `livestream-db`
   - Copy the "Internal Database URL"

5. **Environment Variables**:
   - `DATABASE_URL`: (paste the PostgreSQL URL from step 4)
   - `FLASK_ENV`: `production`
   - `PYTHON_VERSION`: `3.10.11`
   - `ALLOWED_ORIGINS`: `https://your-site-name.netlify.app` (your Netlify URL)

6. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment
   - Copy your backend URL: `https://your-service-name.onrender.com`

7. **Update Frontend**:
   - Go back to Netlify
   - Update `REACT_APP_API_URL` to: `https://your-service-name.onrender.com/api`
   - Trigger redeploy

## Step 3: Test

1. Visit your Netlify URL
2. Try creating an overlay
3. Test stream settings

## Important Notes

⚠️ **FFmpeg Limitation**: Render/Railway/Heroku don't have FFmpeg installed by default.

**Options for RTSP streaming:**
- Use a VPS (DigitalOcean, AWS EC2) for backend
- Use external RTSP-to-HLS service
- Or use web-compatible video URLs (MP4, HLS) directly

## Troubleshooting

**Frontend not loading:**
- Check build logs in Netlify
- Verify `REACT_APP_API_URL` is set

**Backend errors:**
- Check Render logs
- Verify `DATABASE_URL` is correct
- Check CORS settings

**CORS errors:**
- Update `ALLOWED_ORIGINS` in backend with your Netlify URL
- Redeploy backend
