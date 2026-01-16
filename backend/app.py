from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import subprocess
import threading
import time
from pathlib import Path
from dotenv import load_dotenv

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

db = SQLAlchemy(app)

# Overlay Model
class Overlay(db.Model):
    __tablename__ = 'overlays'
    
    id = db.Column(db.Integer, primary_key=True)
    overlay_type = db.Column(db.String(50), nullable=False)  # 'text' or 'image'
    content = db.Column(db.Text, nullable=False)  # Text content or image URL
    position_x = db.Column(db.Float, nullable=False, default=0)
    position_y = db.Column(db.Float, nullable=False, default=0)
    width = db.Column(db.Float, nullable=False, default=100)
    height = db.Column(db.Float, nullable=False, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    rtsp_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    
    # Initialize default stream settings if none exist
    if StreamSettings.query.first() is None:
        default_settings = StreamSettings(rtsp_url='rtsp://example.com/stream')
        db.session.add(default_settings)
        db.session.commit()

# API Routes

# Stream Settings Routes
@app.route('/api/stream/settings', methods=['GET'])
def get_stream_settings():
    settings = StreamSettings.query.first()
    if settings:
        return jsonify(settings.to_dict())
    return jsonify({'rtsp_url': ''}), 200

@app.route('/api/stream/settings', methods=['POST', 'PUT'])
def update_stream_settings():
    data = request.get_json()
    settings = StreamSettings.query.first()
    
    if not settings:
        settings = StreamSettings(rtsp_url=data.get('rtsp_url', ''))
        db.session.add(settings)
    else:
        settings.rtsp_url = data.get('rtsp_url', settings.rtsp_url)
        settings.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(settings.to_dict())

# Overlay CRUD Routes
@app.route('/api/overlays', methods=['GET'])
def get_overlays():
    overlays = Overlay.query.all()
    return jsonify([overlay.to_dict() for overlay in overlays])

@app.route('/api/overlays/<int:overlay_id>', methods=['GET'])
def get_overlay(overlay_id):
    overlay = Overlay.query.get_or_404(overlay_id)
    return jsonify(overlay.to_dict())

@app.route('/api/overlays', methods=['POST'])
def create_overlay():
    data = request.get_json()
    
    overlay = Overlay(
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
def update_overlay(overlay_id):
    overlay = Overlay.query.get_or_404(overlay_id)
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
def delete_overlay(overlay_id):
    overlay = Overlay.query.get_or_404(overlay_id)
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
def get_hls_playlist(stream_id):
    """Serve HLS playlist (.m3u8 file)"""
    settings = db.session.get(StreamSettings, stream_id)
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
def get_hls_segment(stream_id, filename):
    """Serve HLS segment files (.ts files)"""
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
def stop_stream(stream_id):
    """Stop an active stream"""
    stop_ffmpeg_stream(stream_id)
    return jsonify({'message': 'Stream stopped'}), 200

@app.route('/api/stream/status/<int:stream_id>', methods=['GET'])
def get_stream_status(stream_id):
    """Get status of a stream"""
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
