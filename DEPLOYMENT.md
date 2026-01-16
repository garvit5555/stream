# Deployment Guide

This guide covers deploying the Livestream Overlay Manager application.

## Architecture

The application consists of:
- **Frontend**: React app (deploy to Netlify)
- **Backend**: Flask API (deploy to Render/Railway/Heroku)
- **Database**: PostgreSQL (provided by hosting service or external)

## Part 1: Deploy Frontend to Netlify

### Option A: Deploy via GitHub (Recommended)

1. **Push your code to GitHub** (already done ✅)

2. **Go to Netlify**:
   - Visit https://app.netlify.com
   - Sign in with GitHub
   - Click "Add new site" → "Import an existing project"
   - Select your repository: `garvit5555/stream`

3. **Configure Build Settings**:
   - **Base directory**: Leave empty (or set to `frontend` if needed)
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Publish directory**: `frontend/build`

4. **Set Environment Variables**:
   - Go to Site settings → Environment variables
   - Add: `REACT_APP_API_URL` = `https://your-backend-url.com/api`
     (You'll set this after deploying the backend)

5. **Deploy**:
   - Click "Deploy site"
   - Wait for build to complete
   - Your site will be live at `https://your-site-name.netlify.app`

### Option B: Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Build the frontend
cd frontend
npm install
npm run build

# Deploy
cd ..
netlify deploy --prod --dir=frontend/build
```

## Part 2: Deploy Backend to Render (Recommended)

Render is free and easy to use for Flask apps.

### Steps:

1. **Go to Render**: https://render.com
   - Sign up/login with GitHub

2. **Create New Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository: `garvit5555/stream`

3. **Configure Service**:
   - **Name**: `livestream-backend` (or any name)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

4. **Add Environment Variables**:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `FLASK_ENV`: `production`
   - `PYTHON_VERSION`: `3.10` (or your version)

5. **Add PostgreSQL Database**:
   - Click "New" → "PostgreSQL"
   - Create database
   - Copy the connection string
   - Add it as `DATABASE_URL` in environment variables

6. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment
   - Your backend will be at: `https://your-service-name.onrender.com`

7. **Update Frontend API URL**:
   - Go back to Netlify
   - Update `REACT_APP_API_URL` to: `https://your-service-name.onrender.com/api`
   - Trigger a new deployment

## Part 3: Alternative Backend Hosting

### Railway

1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select repository
4. Add PostgreSQL service
5. Set environment variables
6. Deploy

### Heroku

1. Install Heroku CLI
2. Create `Procfile` in backend:
   ```
   web: gunicorn app:app
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql
   heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)
   git push heroku main
   ```

## Important Notes

### FFmpeg on Hosting Services

⚠️ **Important**: Most hosting services (Render, Railway, Heroku) don't have FFmpeg pre-installed.

**Solutions:**

1. **Use a service with FFmpeg**:
   - **DigitalOcean Droplet** (VPS)
   - **AWS EC2**
   - **Google Cloud Compute Engine**
   - **Azure VM**

2. **Add FFmpeg to Render** (if using Render):
   - Add buildpack or install in build command
   - May require custom Docker image

3. **Use external RTSP-to-HLS service**:
   - Use RTSP.me or similar
   - Or run FFmpeg on a separate VPS

### Environment Variables Summary

**Frontend (Netlify)**:
- `REACT_APP_API_URL`: Backend API URL

**Backend (Render/Railway/Heroku)**:
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: `production`
- `PYTHON_VERSION`: `3.10`

### CORS Configuration

The backend already has CORS enabled, but make sure to update it for production:

```python
# In backend/app.py, update CORS if needed:
CORS(app, resources={r"/api/*": {"origins": ["https://your-netlify-site.netlify.app"]}})
```

## Testing Deployment

1. **Test Frontend**: Visit your Netlify URL
2. **Test Backend**: Visit `https://your-backend-url.com/api/overlays`
3. **Test Database**: Create an overlay and verify it saves
4. **Test RTSP**: Enter an RTSP URL and test conversion

## Troubleshooting

### Frontend not connecting to backend:
- Check `REACT_APP_API_URL` environment variable
- Verify CORS settings in backend
- Check browser console for errors

### Backend not starting:
- Check build logs
- Verify all dependencies in requirements.txt
- Check Python version compatibility

### Database connection errors:
- Verify `DATABASE_URL` is correct
- Check database is accessible from hosting service
- Verify SSL requirements

### FFmpeg not found:
- Most cloud services don't include FFmpeg
- Consider using a VPS or external service for RTSP conversion

## Quick Deploy Checklist

- [ ] Frontend deployed to Netlify
- [ ] Backend deployed to Render/Railway/Heroku
- [ ] PostgreSQL database created
- [ ] Environment variables set
- [ ] Frontend API URL updated
- [ ] CORS configured
- [ ] Test all features
- [ ] FFmpeg solution decided (if using RTSP)
