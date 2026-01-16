# Quick Setup Guide

## Prerequisites Check

Make sure you have installed:
- Python 3.8+ (`python --version`)
- Node.js 16+ (`node --version`)
- PostgreSQL 12+ (`psql --version`)
- pip (`pip --version`)
- npm (`npm --version`)

## Step-by-Step Setup

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb livestream_db

# Or using psql:
psql -U postgres
CREATE DATABASE livestream_db;
\q
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp env.example .env

# Edit .env file with your database credentials:
# DATABASE_URL=postgresql://username:password@localhost:5432/livestream_db

# Run the backend server
python app.py
```

The backend will start on `http://localhost:5000`

### 3. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the development server
npm start
```

The frontend will start on `http://localhost:3000`

## Testing the Application

1. Open `http://localhost:3000` in your browser
2. Click "Stream Settings" and enter an RTSP URL (or use a test stream)
3. Click "Add Overlay" to create a text or image overlay
4. Drag overlays on the video to reposition them
5. Resize overlays using the handle in the bottom-right corner
6. Use Play/Pause and Volume controls to manage playback

## RTSP Stream Testing

For testing, you can use:
- **RTSP.me**: Provides web-compatible URLs from RTSP streams
- **Test RTSP URLs**: Some public test streams are available online
- **Local RTSP**: If you have a local RTSP source, you'll need to convert it to HLS/WebRTC

Note: Browsers cannot play RTSP directly. The application expects web-compatible formats (HLS, DASH, or direct video URLs).

## Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running: `pg_isready`
- Check database credentials in `.env` file
- Ensure database exists: `psql -l | grep livestream_db`

### Backend Not Starting
- Check if port 5000 is available
- Verify all dependencies are installed: `pip list`
- Check for Python version compatibility

### Frontend Not Starting
- Check if port 3000 is available
- Verify Node modules: `npm list`
- Clear cache: `npm cache clean --force` then `npm install`

### Overlays Not Appearing
- Check browser console for errors
- Verify backend API is running and accessible
- Check network tab for API calls
