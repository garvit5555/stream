# Livestream Overlay Manager

A web application for managing livestream videos with customizable overlays. Built with Flask (Python), PostgreSQL, and React.

## 🌐 Live Demo

**Try it now:** [https://livestreamx.netlify.app/](https://livestreamx.netlify.app/)

![Livestream Overlay Manager](./images/example.jpeg)

## Features

- **Livestream Playback**: Play RTSP streams with automatic HLS conversion for browser compatibility
- **RTSP to HLS Conversion**: Automatic conversion of RTSP streams to HLS format using FFmpeg
- **Overlay Management**: Create, edit, and delete text and image overlays
- **Drag & Drop**: Move overlays freely on the video
- **Resizable Overlays**: Adjust overlay size dynamically
- **Real-time Updates**: Overlays update in real-time on the livestream view
- **CRUD APIs**: Full REST API for managing overlays and stream settings

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: React
- **Video Streaming**: RTSP-compatible (requires conversion to HLS/WebRTC for browser playback)

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- pip and npm

## Setup Instructions

### 1. Database Setup

Create a PostgreSQL database:

```bash
createdb livestream_db
```

Or using psql:

```sql
CREATE DATABASE livestream_db;
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```
DATABASE_URL=postgresql://username:password@localhost:5432/livestream_db
```

Run the backend:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`

## RTSP Streaming

**The application now includes automatic RTSP to HLS conversion!**

When you enter an RTSP URL, the backend automatically converts it to HLS format using FFmpeg, making it playable in browsers.

### Requirements:
- **FFmpeg must be installed** on your system
- See [RTSP_SETUP.md](RTSP_SETUP.md) for detailed setup instructions

### Quick Start:
1. Install FFmpeg (see RTSP_SETUP.md)
2. Enter your RTSP URL in Stream Settings
3. The video will automatically convert and play

### Alternative Options:
- **Use web-compatible URLs**: Direct MP4, HLS (.m3u8), or DASH streams
- **Use RTSP.me**: For testing, convert RTSP to web-compatible format

## API Endpoints

### Stream Settings
- `GET /api/stream/settings` - Get current stream settings
- `POST /api/stream/settings` - Update stream settings

### Overlays
- `GET /api/overlays` - Get all overlays
- `GET /api/overlays/<id>` - Get a specific overlay
- `POST /api/overlays` - Create a new overlay
- `PUT /api/overlays/<id>` - Update an overlay
- `DELETE /api/overlays/<id>` - Delete an overlay

## Project Structure

```
.
├── backend/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── App.js          # Main app component
│   └── package.json        # Node dependencies
└── README.md
```

## 🚀 Live Deployment

- **Frontend:** [https://livestreamx.netlify.app/](https://livestreamx.netlify.app/)
- **Backend API:** [https://livestream-backend-tdes.onrender.com/api](https://livestream-backend-tdes.onrender.com/api)

The application is fully deployed and ready to use! Just visit the frontend URL to start managing overlays on your livestream.

## Usage

1. Visit [https://livestreamx.netlify.app/](https://livestreamx.netlify.app/) or run locally:
2. Start the backend server (if running locally)
3. Start the frontend development server (if running locally)
4. Open the application in your browser
5. Configure the RTSP stream URL in Stream Settings
6. Add overlays using the "Add Overlay" button
7. Drag and resize overlays directly on the video
8. Use Play/Pause and Volume controls to manage playback

## Development

### Backend Development

The Flask app runs in debug mode by default. Database migrations are handled automatically via SQLAlchemy.

### Frontend Development

The React app uses Create React App. Hot reloading is enabled in development mode.

## License

MIT
