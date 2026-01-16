# RTSP to HLS Conversion Setup

This application now supports automatic conversion of RTSP streams to HLS format for browser playback.

## Prerequisites

### 1. Install FFmpeg

FFmpeg is required for RTSP to HLS conversion. Install it based on your operating system:

#### Windows:
1. Download FFmpeg from: https://ffmpeg.org/download.html
2. Or use chocolatey: `choco install ffmpeg`
3. Or download from: https://www.gyan.dev/ffmpeg/builds/
4. Extract and add FFmpeg to your system PATH

#### macOS:
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Verify Installation:
```bash
ffmpeg -version
```

You should see FFmpeg version information if installed correctly.

## How It Works

1. **User enters RTSP URL** in Stream Settings
2. **Backend detects RTSP URL** and starts FFmpeg conversion
3. **FFmpeg converts RTSP to HLS** format (.m3u8 playlist + .ts segments)
4. **Frontend requests HLS stream** from backend endpoint
5. **Browser plays HLS stream** natively

## Usage

1. **Start the backend server:**
   ```bash
   cd backend
   python app.py
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm start
   ```

3. **Configure RTSP stream:**
   - Click "Stream Settings" in the app
   - Enter your RTSP URL (e.g., `rtsp://username:password@ip:port/stream`)
   - Click "Save Settings"

4. **The video should start playing automatically** after a few seconds (FFmpeg needs time to generate the first segment)

## API Endpoints

### Get HLS Playlist
```
GET /api/stream/hls/<stream_id>
```
Returns the HLS playlist (.m3u8 file) for the stream.

### Get HLS Segment
```
GET /api/stream/hls/<stream_id>/<filename>
```
Returns individual HLS segment files (.ts files).

### Stop Stream
```
POST /api/stream/stop/<stream_id>
```
Stops the FFmpeg conversion process for a stream.

### Get Stream Status
```
GET /api/stream/status/<stream_id>
```
Returns the current status of a stream (running/stopped).

## Troubleshooting

### "FFmpeg not found" error
- Ensure FFmpeg is installed and in your system PATH
- Verify with: `ffmpeg -version`
- Restart the backend server after installing FFmpeg

### Video not playing
- Check browser console for errors
- Verify RTSP URL is correct and accessible
- Check backend logs for FFmpeg errors
- Ensure RTSP stream is using TCP transport (configured in code)

### High latency
- HLS segments are 2 seconds by default
- This is normal for HLS streaming
- For lower latency, consider WebRTC (more complex)

### Stream stops after a while
- Check FFmpeg process in backend logs
- Ensure RTSP source is stable
- Check network connectivity

## Technical Details

- **Segment Duration:** 2 seconds
- **Playlist Size:** 5 segments (keeps last 5 segments)
- **Video Codec:** H.264 (libx264)
- **Audio Codec:** AAC
- **Transport:** TCP (for better reliability)

## File Structure

HLS files are stored in `backend/hls_output/`:
- `stream_<id>.m3u8` - Playlist file
- `stream_<id>_000.ts` - Video segments
- `stream_<id>_001.ts` - Video segments
- etc.

These files are automatically cleaned up when streams stop.

## Notes

- Each RTSP stream conversion runs as a separate FFmpeg process
- Multiple streams can run simultaneously
- Old segments are automatically deleted to save disk space
- The conversion starts automatically when the HLS endpoint is first accessed
