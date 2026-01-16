import React from 'react';
import './OverlayManager.css';

const OverlayManager = ({ overlays, onEdit, onDelete }) => {
  return (
    <div className="overlay-manager">
      <h2>Overlays ({overlays.length})</h2>
      {overlays.length === 0 ? (
        <p className="empty-message">No overlays yet. Click "Add Overlay" to create one.</p>
      ) : (
        <div className="overlay-list">
          {overlays.map((overlay) => (
            <div key={overlay.id} className="overlay-item">
              <div className="overlay-item-header">
                <span className="overlay-item-title">
                  {overlay.overlay_type === 'text' ? '📝 Text' : '🖼️ Image'}
                </span>
                <div className="overlay-item-actions">
                  <button
                    onClick={() => onEdit(overlay)}
                    className="btn btn-small btn-secondary"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(overlay.id)}
                    className="btn btn-small btn-danger"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="overlay-item-content">
                {overlay.overlay_type === 'text' ? (
                  <div className="overlay-preview-text">{overlay.content}</div>
                ) : (
                  <div className="overlay-preview-image">
                    <img src={overlay.content} alt="Preview" onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }} />
                    <span style={{ display: 'none' }}>Invalid image URL</span>
                  </div>
                )}
              </div>
              <div className="overlay-item-meta">
                Position: ({Math.round(overlay.position_x)}, {Math.round(overlay.position_y)}) | 
                Size: {Math.round(overlay.width)} × {Math.round(overlay.height)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default OverlayManager;
