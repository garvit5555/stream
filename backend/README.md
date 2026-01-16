# Livestream Backend API

Flask backend for managing livestream overlays and settings.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a PostgreSQL database:
```bash
createdb livestream_db
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

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
