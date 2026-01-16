import React, { useState } from 'react';
import './StreamSettings.css';

const StreamSettings = ({ currentUrl, onSubmit, onCancel }) => {
  const [rtspUrl, setRtspUrl] = useState(currentUrl);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(rtspUrl);
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Stream Settings</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="rtsp_url">RTSP URL</label>
            <input
              type="text"
              id="rtsp_url"
              value={rtspUrl}
              onChange={(e) => setRtspUrl(e.target.value)}
              placeholder="rtsp://example.com/stream"
              required
            />
            <small className="form-hint">
              Enter the RTSP stream URL. Note: RTSP streams need to be converted to HLS or WebRTC for browser playback.
              You can use services like RTSP.me or set up a backend proxy.
            </small>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onCancel} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Save Settings
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StreamSettings;
