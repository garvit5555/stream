import React, { useState, useEffect } from 'react';
import './App.css';
import VideoPlayer from './components/VideoPlayer';
import OverlayManager from './components/OverlayManager';
import OverlayForm from './components/OverlayForm';
import StreamSettings from './components/StreamSettings';
import { getOverlays, createOverlay, updateOverlay, deleteOverlay, getStreamSettings, updateStreamSettings } from './services/api';

function App() {
  const [overlays, setOverlays] = useState([]);
  const [streamUrl, setStreamUrl] = useState('');
  const [streamSettings, setStreamSettings] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingOverlay, setEditingOverlay] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    loadOverlays();
    loadStreamSettings();
  }, []);

  const loadOverlays = async () => {
    try {
      const data = await getOverlays();
      setOverlays(data);
    } catch (error) {
      console.error('Error loading overlays:', error);
    }
  };

  const loadStreamSettings = async () => {
    try {
      const settings = await getStreamSettings();
      setStreamSettings(settings);
      setStreamUrl(settings.rtsp_url || '');
    } catch (error) {
      console.error('Error loading stream settings:', error);
    }
  };

  const handleCreateOverlay = async (overlayData) => {
    try {
      const newOverlay = await createOverlay(overlayData);
      setOverlays([...overlays, newOverlay]);
      setShowForm(false);
    } catch (error) {
      console.error('Error creating overlay:', error);
      alert('Failed to create overlay');
    }
  };

  const handleUpdateOverlay = async (id, overlayData) => {
    try {
      const updated = await updateOverlay(id, overlayData);
      setOverlays(overlays.map(o => o.id === id ? updated : o));
      setEditingOverlay(null);
    } catch (error) {
      console.error('Error updating overlay:', error);
      alert('Failed to update overlay');
    }
  };

  const handleDeleteOverlay = async (id) => {
    if (window.confirm('Are you sure you want to delete this overlay?')) {
      try {
        await deleteOverlay(id);
        setOverlays(overlays.filter(o => o.id !== id));
      } catch (error) {
        console.error('Error deleting overlay:', error);
        alert('Failed to delete overlay');
      }
    }
  };

  const handleOverlayPositionChange = async (id, position) => {
    const overlay = overlays.find(o => o.id === id);
    if (overlay) {
      await handleUpdateOverlay(id, {
        ...overlay,
        position_x: position.x,
        position_y: position.y
      });
    }
  };

  const handleOverlaySizeChange = async (id, size) => {
    const overlay = overlays.find(o => o.id === id);
    if (overlay) {
      await handleUpdateOverlay(id, {
        ...overlay,
        width: size.width,
        height: size.height
      });
    }
  };

  const handleStreamSettingsUpdate = async (rtspUrl) => {
    try {
      await updateStreamSettings({ rtsp_url: rtspUrl });
      setStreamUrl(rtspUrl);
      setShowSettings(false);
    } catch (error) {
      console.error('Error updating stream settings:', error);
      alert('Failed to update stream settings');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Livestream Overlay Manager</h1>
        <div className="header-actions">
          <button onClick={() => setShowSettings(true)} className="btn btn-secondary">
            Stream Settings
          </button>
          <button onClick={() => setShowForm(true)} className="btn btn-primary">
            Add Overlay
          </button>
        </div>
      </header>

      <main className="App-main">
        <div className="video-container">
          <VideoPlayer
            streamUrl={streamUrl}
            streamSettings={streamSettings}
            overlays={overlays}
            onOverlayPositionChange={handleOverlayPositionChange}
            onOverlaySizeChange={handleOverlaySizeChange}
          />
        </div>

        <div className="overlay-list-container">
          <OverlayManager
            overlays={overlays}
            onEdit={setEditingOverlay}
            onDelete={handleDeleteOverlay}
          />
        </div>
      </main>

      {showForm && (
        <OverlayForm
          onSubmit={handleCreateOverlay}
          onCancel={() => setShowForm(false)}
        />
      )}

      {editingOverlay && (
        <OverlayForm
          overlay={editingOverlay}
          onSubmit={(data) => handleUpdateOverlay(editingOverlay.id, data)}
          onCancel={() => setEditingOverlay(null)}
        />
      )}

      {showSettings && (
        <StreamSettings
          currentUrl={streamUrl}
          onSubmit={handleStreamSettingsUpdate}
          onCancel={() => setShowSettings(false)}
        />
      )}
    </div>
  );
}

export default App;
