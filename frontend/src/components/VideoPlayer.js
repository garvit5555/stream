import React, { useRef, useEffect, useState } from 'react';
import Draggable from 'react-draggable';
import { Resizable } from 'react-resizable';
import 'react-resizable/css/styles.css';
import { getHLSStreamUrl } from '../services/api';
import './VideoPlayer.css';

const VideoPlayer = ({ streamUrl, streamSettings, overlays, onOverlayPositionChange, onOverlaySizeChange }) => {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(1);
  const [videoUrl, setVideoUrl] = useState('');
  const [streamError, setStreamError] = useState('');

  // Convert RTSP to HLS or use a proxy
  useEffect(() => {
    if (streamUrl) {
      setStreamError('');
      
      // If the URL is already web-compatible (HLS, DASH, MP4, etc.), use it directly
      if (streamUrl.startsWith('http://') || streamUrl.startsWith('https://')) {
        setVideoUrl(streamUrl);
      } 
      // If it's an RTSP URL, use the backend HLS conversion endpoint
      else if (streamUrl.startsWith('rtsp://') && streamSettings && streamSettings.id) {
        const hlsUrl = getHLSStreamUrl(streamSettings.id);
        console.log('Converting RTSP to HLS:', hlsUrl);
        setVideoUrl(hlsUrl);
      } 
      else {
        if (streamUrl.startsWith('rtsp://')) {
          setStreamError('Stream settings not loaded. Please wait...');
        }
        setVideoUrl('');
      }
    } else {
      setVideoUrl('');
      setStreamError('');
    }
  }, [streamUrl, streamSettings]);

  const handlePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
  };

  const handleOverlayDrag = (id, data) => {
    onOverlayPositionChange(id, { x: data.x, y: data.y });
  };

  const handleOverlayResize = (id, { size }) => {
    onOverlaySizeChange(id, { width: size.width, height: size.height });
  };

  return (
    <div className="video-player-container">
      <div className="video-wrapper">
        {videoUrl ? (
          <video
            ref={videoRef}
            src={videoUrl}
            className="video-element"
            controls={false}
            playsInline
            onError={(e) => {
              console.error('Video playback error:', e);
              setStreamError('Failed to load video stream. Please check the RTSP URL and ensure FFmpeg is installed.');
            }}
            onLoadStart={() => {
              console.log('Video loading started');
              setStreamError('');
            }}
          />
        ) : (
          <div className="video-placeholder">
            <p>{streamError || 'No stream URL configured'}</p>
            <p className="video-placeholder-hint">
              {streamError ? (
                'Loading stream...'
              ) : (
                <>
                  Please configure an RTSP URL in Stream Settings.
                  <br />
                  RTSP streams will be automatically converted to HLS format.
                </>
              )}
            </p>
          </div>
        )}
        
        {/* Render overlays */}
        {overlays.map((overlay) => (
          <Draggable
            key={overlay.id}
            position={{ x: overlay.position_x, y: overlay.position_y }}
            onStop={(e, data) => handleOverlayDrag(overlay.id, data)}
            bounds="parent"
          >
            <div style={{ position: 'absolute', zIndex: 100 }}>
              <Resizable
                width={overlay.width}
                height={overlay.height}
                onResize={(e, { size }) => handleOverlayResize(overlay.id, { size })}
                minConstraints={[50, 30]}
                maxConstraints={[800, 600]}
              >
                <div
                  className={`overlay-element overlay-${overlay.overlay_type}`}
                  style={{
                    width: overlay.width,
                    height: overlay.height,
                  }}
                >
                  {overlay.overlay_type === 'text' ? (
                    <div className="overlay-text">{overlay.content}</div>
                  ) : (
                    <>
                      <img
                        src={overlay.content}
                        alt="Overlay"
                        className="overlay-image"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          if (e.target.nextSibling) {
                            e.target.nextSibling.style.display = 'block';
                          }
                        }}
                      />
                      <div className="overlay-label" style={{ display: 'none' }}>
                        Image failed to load
                      </div>
                    </>
                  )}
                </div>
              </Resizable>
            </div>
          </Draggable>
        ))}
      </div>

      <div className="video-controls">
        <button onClick={handlePlay} className="control-btn">
          {isPlaying ? '⏸ Pause' : '▶ Play'}
        </button>
        <div className="volume-control">
          <label>Volume:</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={handleVolumeChange}
          />
          <span>{Math.round(volume * 100)}%</span>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;
