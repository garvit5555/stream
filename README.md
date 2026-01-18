# Livestream Overlay Manager

A web application for managing livestream videos with customizable overlays. Built with Flask (Python), PostgreSQL, and React.

## 🌐 Live Demo

**Try it now:** [https://livestreamx.netlify.app/](https://livestreamx.netlify.app/)

### Login Page

![Login Page](./images/login-page.png)

The application features a secure login/registration system. Users must create an account to access their personalized overlay management interface.

## Features

- **🔐 JWT Authentication**: Secure user registration and login with JWT tokens
- **👥 Multi-User Support**: Each user has their own isolated overlays and stream settings
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

Edit `.env` with your database credentials and secret key:

```
DATABASE_URL=postgresql://username:password@localhost:5432/livestream_db
SECRET_KEY=your-secret-key-here-change-in-production
```

**Important:** Generate a strong random string for `SECRET_KEY` (used for JWT token signing).

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

## 🔐 Authentication

The application uses JWT (JSON Web Tokens) for secure authentication. Each user has their own isolated data.

### User Registration & Login

![Login Interface](./images/login-page.png)

**Features:**
- Secure password hashing using Werkzeug
- JWT token-based authentication
- Token expiration after 7 days
- User-specific data isolation

**How it works:**
1. Users register with username, email, and password
2. Upon successful registration/login, a JWT token is issued
3. Token is stored in browser localStorage
4. All API requests include the token in the Authorization header
5. Each user can only access their own overlays and stream settings

For detailed authentication documentation, see [AUTHENTICATION.md](AUTHENTICATION.md)

## API Endpoints

### Authentication (Public)
- `POST /api/auth/register` - Register a new user
  - Body: `{ "username": "...", "email": "...", "password": "..." }`
- `POST /api/auth/login` - Login user
  - Body: `{ "username": "...", "password": "..." }`
- `GET /api/auth/me` - Get current user info (requires authentication)

### Stream Settings (Protected - Requires Authentication)
- `GET /api/stream/settings` - Get current user's stream settings
- `POST /api/stream/settings` - Update current user's stream settings

### Overlays (Protected - Requires Authentication)
- `GET /api/overlays` - Get all overlays for current user
- `GET /api/overlays/<id>` - Get a specific overlay (must belong to user)
- `POST /api/overlays` - Create a new overlay for current user
- `PUT /api/overlays/<id>` - Update an overlay (must belong to user)
- `DELETE /api/overlays/<id>` - Delete an overlay (must belong to user)

**Note:** All protected endpoints require an `Authorization: Bearer <token>` header.

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

- **Frontend:** Deployed on Netlify
- **Backend API:** Deployed on Render

The application is fully deployed and ready to use! Just visit the frontend URL to start managing overlays on your livestream.

## Usage

1. Visit [https://livestreamx.netlify.app/](https://livestreamx.netlify.app/) or run locally
2. **Register a new account** or **login** if you already have one
3. Start the backend server (if running locally)
4. Start the frontend development server (if running locally)
5. Open the application in your browser
6. Configure the RTSP stream URL in Stream Settings
7. Add overlays using the "Add Overlay" button
8. Drag and resize overlays directly on the video
9. Use Play/Pause and Volume controls to manage playback

**Note:** Each user account has its own isolated overlays and stream settings. Multiple users can use the application simultaneously without interfering with each other's data.

## Development

### Backend Development

The Flask app runs in debug mode by default. Database migrations are handled automatically via SQLAlchemy.

### Frontend Development

The React app uses Create React App. Hot reloading is enabled in development mode.

## License

MIT
