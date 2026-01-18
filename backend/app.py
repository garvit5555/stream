from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import subprocess
import threading
import time
from pathlib import Path
from dotenv import load_dotenv
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

load_dotenv()

app = Flask(__name__)
# Configure CORS - update with your Netlify URL in production
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv("ALLOWED_ORIGINS", "*").split(","),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# HLS output directory
HLS_OUTPUT_DIR = Path('hls_output')
HLS_OUTPUT_DIR.mkdir(exist_ok=True)

# Store active FFmpeg processes
active_streams = {}
stream_lock = threading.Lock()

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/livestream_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

db = SQLAlchemy(app)

# JWT Configuration
JWT_SECRET_KEY = app.config['SECRET_KEY']
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = timedelta(days=7)

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Overlay Model
class Overlay(db.Model):
    __tablename__ = 'overlays'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    overlay_type = db.Column(db.String(50), nullable=False)  # 'text' or 'image'
    content = db.Column(db.Text, nullable=False)  # Text content or image URL
    position_x = db.Column(db.Float, nullable=False, default=0)
    position_y = db.Column(db.Float, nullable=False, default=0)
    width = db.Column(db.Float, nullable=False, default=100)
    height = db.Column(db.Float, nullable=False, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='overlays')
    
    def to_dict(self):
        return {
            'id': self.id,
            'overlay_type': self.overlay_type,
            'content': self.content,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Stream Settings Model
class StreamSettings(db.Model):
    __tablename__ = 'stream_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    rtsp_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='stream_settings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'rtsp_url': self.rtsp_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Create tables
with app.app_context():
    db.create_all()

# JWT Helper Functions
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        current_user_id = payload['user_id']
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# API Routes

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Generate token
    token = generate_token(user.id)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Generate token
    token = generate_token(user.id)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user_id):
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200

# Database Migration Endpoint (One-time use)
@app.route('/api/migrate', methods=['POST'])
def run_migration():
    """
    One-time migration endpoint to add user_id columns to existing tables.
    Can be called multiple times safely (idempotent).
    Optional: Add MIGRATION_SECRET in env for security.
    """
    from sqlalchemy import text
    
    # Optional security check
    migration_secret = os.getenv('MIGRATION_SECRET')
    if migration_secret:
        provided_secret = request.headers.get('X-Migration-Secret') or request.json.get('secret') if request.is_json else None
        if provided_secret != migration_secret:
            return jsonify({'error': 'Invalid migration secret'}), 401
    
    results = {
        'success': True,
        'steps': [],
        'errors': []
    }
    
    try:
        # Create users table if it doesn't exist
        db.create_all()
        results['steps'].append('Users table created/verified')
        
        # Check if user_id column exists in overlays table
        try:
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='overlays' AND column_name='user_id'
            """))
            overlay_has_user_id = result.fetchone() is not None
        except Exception as e:
            overlay_has_user_id = False
            results['errors'].append(f"Error checking overlays: {str(e)}")
        
        # Check if user_id column exists in stream_settings table
        try:
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='stream_settings' AND column_name='user_id'
            """))
            settings_has_user_id = result.fetchone() is not None
        except Exception as e:
            settings_has_user_id = False
            results['errors'].append(f"Error checking stream_settings: {str(e)}")
        
        # Add user_id to overlays if it doesn't exist
        if not overlay_has_user_id:
            try:
                db.session.execute(text("""
                    ALTER TABLE overlays 
                    ADD COLUMN user_id INTEGER REFERENCES users(id)
                """))
                db.session.commit()
                results['steps'].append('Added user_id column to overlays table')
            except Exception as e:
                results['errors'].append(f"Error adding user_id to overlays: {str(e)}")
                db.session.rollback()
        else:
            results['steps'].append('overlays table already has user_id column')
        
        # Add user_id to stream_settings if it doesn't exist
        if not settings_has_user_id:
            try:
                # First add as nullable
                db.session.execute(text("""
                    ALTER TABLE stream_settings 
                    ADD COLUMN user_id INTEGER REFERENCES users(id)
                """))
                db.session.commit()
                results['steps'].append('Added user_id column to stream_settings table')
                
                # Delete existing stream_settings that don't have user_id
                result = db.session.execute(text("""
                    DELETE FROM stream_settings WHERE user_id IS NULL
                """))
                db.session.commit()
                deleted_count = result.rowcount
                if deleted_count > 0:
                    results['steps'].append(f'Cleaned up {deleted_count} orphaned stream_settings')
                
                # Now make it NOT NULL and UNIQUE
                db.session.execute(text("""
                    ALTER TABLE stream_settings 
                    ALTER COLUMN user_id SET NOT NULL
                """))
                db.session.execute(text("""
                    ALTER TABLE stream_settings 
                    ADD CONSTRAINT stream_settings_user_id_unique UNIQUE (user_id)
                """))
                db.session.commit()
                results['steps'].append('Made user_id NOT NULL and UNIQUE in stream_settings')
            except Exception as e:
                results['errors'].append(f"Error adding user_id to stream_settings: {str(e)}")
                db.session.rollback()
        else:
            results['steps'].append('stream_settings table already has user_id column')
        
        # Clean up overlays without user_id
        try:
            result = db.session.execute(text("""
                DELETE FROM overlays WHERE user_id IS NULL
            """))
            db.session.commit()
            deleted_count = result.rowcount
            if deleted_count > 0:
                results['steps'].append(f'Cleaned up {deleted_count} orphaned overlays')
        except Exception as e:
            results['errors'].append(f"Could not clean up overlays: {str(e)}")
        
        # Make user_id NOT NULL in overlays if it's nullable
        try:
            db.session.execute(text("""
                ALTER TABLE overlays 
                ALTER COLUMN user_id SET NOT NULL
            """))
            db.session.commit()
            results['steps'].append('Made user_id NOT NULL in overlays')
        except Exception as e:
            # Column might already be NOT NULL or have NULL values
            results['errors'].append(f"Could not set user_id to NOT NULL in overlays: {str(e)}")
            db.session.rollback()
        
        if results['errors']:
            results['success'] = False
        
        return jsonify(results), 200 if results['success'] else 500
        
    except Exception as e:
        results['success'] = False
        results['errors'].append(f"Migration failed: {str(e)}")
        return jsonify(results), 500

# Stream Settings Routes
@app.route('/api/stream/settings', methods=['GET'])
@token_required
def get_stream_settings(current_user_id):
    settings = StreamSettings.query.filter_by(user_id=current_user_id).first()
    if settings:
        return jsonify(settings.to_dict())
    return jsonify({'rtsp_url': ''}), 200

@app.route('/api/stream/settings', methods=['POST', 'PUT'])
@token_required
def update_stream_settings(current_user_id):
    data = request.get_json()
    settings = StreamSettings.query.filter_by(user_id=current_user_id).first()
    
    if not settings:
        settings = StreamSettings(user_id=current_user_id, rtsp_url=data.get('rtsp_url', ''))
        db.session.add(settings)
    else:
        settings.rtsp_url = data.get('rtsp_url', settings.rtsp_url)
        settings.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(settings.to_dict())

# Overlay CRUD Routes
@app.route('/api/overlays', methods=['GET'])
@token_required
def get_overlays(current_user_id):
    overlays = Overlay.query.filter_by(user_id=current_user_id).all()
    return jsonify([overlay.to_dict() for overlay in overlays])

@app.route('/api/overlays/<int:overlay_id>', methods=['GET'])
@token_required
def get_overlay(current_user_id, overlay_id):
    overlay = Overlay.query.filter_by(id=overlay_id, user_id=current_user_id).first_or_404()
    return jsonify(overlay.to_dict())

@app.route('/api/overlays', methods=['POST'])
@token_required
def create_overlay(current_user_id):
    data = request.get_json()
    
    overlay = Overlay(
        user_id=current_user_id,
        overlay_type=data.get('overlay_type', 'text'),
        content=data.get('content', ''),
        position_x=data.get('position_x', 0),
        position_y=data.get('position_y', 0),
        width=data.get('width', 100),
        height=data.get('height', 50)
    )
    
    db.session.add(overlay)
    db.session.commit()
    return jsonify(overlay.to_dict()), 201

@app.route('/api/overlays/<int:overlay_id>', methods=['PUT'])
@token_required
def update_overlay(current_user_id, overlay_id):
    overlay = Overlay.query.filter_by(id=overlay_id, user_id=current_user_id).first_or_404()
    data = request.get_json()
    
    overlay.overlay_type = data.get('overlay_type', overlay.overlay_type)
    overlay.content = data.get('content', overlay.content)
    overlay.position_x = data.get('position_x', overlay.position_x)
    overlay.position_y = data.get('position_y', overlay.position_y)
    overlay.width = data.get('width', overlay.width)
    overlay.height = data.get('height', overlay.height)
    overlay.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(overlay.to_dict())

@app.route('/api/overlays/<int:overlay_id>', methods=['DELETE'])
@token_required
def delete_overlay(current_user_id, overlay_id):
    overlay = Overlay.query.filter_by(id=overlay_id, user_id=current_user_id).first_or_404()
    db.session.delete(overlay)
    db.session.commit()
    return jsonify({'message': 'Overlay deleted successfully'}), 200

# RTSP to HLS Conversion Routes
def start_ffmpeg_stream(rtsp_url, stream_id):
    """Start FFmpeg process to convert RTSP to HLS"""
    playlist_path = HLS_OUTPUT_DIR / f'stream_{stream_id}.m3u8'
    segment_path = HLS_OUTPUT_DIR / f'stream_{stream_id}_%03d.ts'
    
    # FFmpeg command to convert RTSP to HLS
    ffmpeg_cmd = [
        'ffmpeg',
        '-rtsp_transport', 'tcp',  # Use TCP for better reliability
        '-i', rtsp_url,
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-tune', 'zerolatency',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-f', 'hls',
        '-hls_time', '2',  # 2 second segments
        '-hls_list_size', '5',  # Keep 5 segments in playlist
        '-hls_flags', 'delete_segments+append_list',  # Delete old segments
        '-hls_segment_filename', str(segment_path),
        '-hls_playlist_type', 'event',
        '-start_number', '0',
        str(playlist_path)
    ]
    
    try:
        print(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Start a thread to log FFmpeg output
        def log_output():
            if process.stderr:
                for line in iter(process.stderr.readline, b''):
                    if line:
                        print(f"FFmpeg: {line.decode().strip()}")
        
        log_thread = threading.Thread(target=log_output, daemon=True)
        log_thread.start()
        
        with stream_lock:
            active_streams[stream_id] = {
                'process': process,
                'playlist_path': playlist_path,
                'started_at': time.time()
            }
        
        print(f"FFmpeg process started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"Error starting FFmpeg: {e}")
        import traceback
        traceback.print_exc()
        return None

def stop_ffmpeg_stream(stream_id):
    """Stop FFmpeg process for a stream"""
    with stream_lock:
        if stream_id in active_streams:
            process = active_streams[stream_id]['process']
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
            del active_streams[stream_id]
            
            # Clean up HLS files
            for file in HLS_OUTPUT_DIR.glob(f'stream_{stream_id}*'):
                try:
                    file.unlink()
                except:
                    pass

@app.route('/api/stream/hls/<int:stream_id>')
@token_required
def get_hls_playlist(current_user_id, stream_id):
    """Serve HLS playlist (.m3u8 file)"""
    settings = StreamSettings.query.filter_by(id=stream_id, user_id=current_user_id).first()
    if not settings:
        return jsonify({'error': 'Stream not found'}), 404
    
    playlist_path = HLS_OUTPUT_DIR / f'stream_{stream_id}.m3u8'
    
    # Check if stream is already running
    with stream_lock:
        if stream_id not in active_streams:
            # Start FFmpeg conversion
            rtsp_url = settings.rtsp_url
            if not rtsp_url.startswith('rtsp://'):
                return jsonify({'error': 'Invalid RTSP URL'}), 400
            
            print(f"Starting FFmpeg conversion for RTSP: {rtsp_url}")
            process = start_ffmpeg_stream(rtsp_url, stream_id)
            if not process:
                print("Failed to start FFmpeg process")
                return jsonify({'error': 'Failed to start stream conversion'}), 500
            
            # Wait a moment for first segment
            print("Waiting for first HLS segment...")
            time.sleep(5)
    
    # Serve the playlist file
    if playlist_path.exists():
        # Read and fix segment URLs in playlist
        try:
            with open(playlist_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix segment URLs to use absolute paths
            lines = content.split('\n')
            fixed_lines = []
            for line in lines:
                if line.endswith('.ts') and not line.startswith('http'):
                    # Make segment URL absolute
                    fixed_lines.append(f'/api/stream/hls/{stream_id}/{line}')
                else:
                    fixed_lines.append(line)
            
            fixed_content = '\n'.join(fixed_lines)
            
            return Response(
                fixed_content,
                mimetype='application/vnd.apple.mpegurl',
                headers={
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/vnd.apple.mpegurl'
                }
            )
        except Exception as e:
            print(f"Error reading playlist: {e}")
            return jsonify({'error': f'Error reading playlist: {str(e)}'}), 500
    else:
        print(f"Playlist not found at: {playlist_path}")
        # Check if FFmpeg process is still running
        with stream_lock:
            if stream_id in active_streams:
                process = active_streams[stream_id]['process']
                if process.poll() is not None:
                    print(f"FFmpeg process exited with code: {process.returncode}")
                    # Try to read stderr
                    try:
                        stderr_output = process.stderr.read().decode() if process.stderr else "No stderr"
                        print(f"FFmpeg error: {stderr_output}")
                    except:
                        pass
        
        return jsonify({'error': 'Playlist not ready yet. Please wait a few seconds and try again.'}), 503

@app.route('/api/stream/hls/<int:stream_id>/<filename>')
@token_required
def get_hls_segment(current_user_id, stream_id, filename):
    """Serve HLS segment files (.ts files)"""
    # Verify stream belongs to user
    settings = StreamSettings.query.filter_by(id=stream_id, user_id=current_user_id).first()
    if not settings:
        return jsonify({'error': 'Stream not found'}), 404
    
    segment_path = HLS_OUTPUT_DIR / filename
    
    if segment_path.exists():
        return send_file(
            segment_path,
            mimetype='video/mp2t',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600'
            }
        )
    else:
        return jsonify({'error': 'Segment not found'}), 404

@app.route('/api/stream/stop/<int:stream_id>', methods=['POST'])
@token_required
def stop_stream(current_user_id, stream_id):
    """Stop an active stream"""
    # Verify stream belongs to user
    settings = StreamSettings.query.filter_by(id=stream_id, user_id=current_user_id).first()
    if not settings:
        return jsonify({'error': 'Stream not found'}), 404
    
    stop_ffmpeg_stream(stream_id)
    return jsonify({'message': 'Stream stopped'}), 200

@app.route('/api/stream/status/<int:stream_id>', methods=['GET'])
@token_required
def get_stream_status(current_user_id, stream_id):
    """Get status of a stream"""
    # Verify stream belongs to user
    settings = StreamSettings.query.filter_by(id=stream_id, user_id=current_user_id).first()
    if not settings:
        return jsonify({'error': 'Stream not found'}), 404
    
    with stream_lock:
        if stream_id in active_streams:
            process = active_streams[stream_id]['process']
            is_running = process.poll() is None
            return jsonify({
                'running': is_running,
                'started_at': active_streams[stream_id]['started_at']
            })
        return jsonify({'running': False}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
