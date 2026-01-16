import React, { useState, useEffect } from 'react';
import './OverlayForm.css';

const OverlayForm = ({ overlay, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    overlay_type: 'text',
    content: '',
    position_x: 0,
    position_y: 0,
    width: 100,
    height: 50,
  });

  useEffect(() => {
    if (overlay) {
      setFormData({
        overlay_type: overlay.overlay_type || 'text',
        content: overlay.content || '',
        position_x: overlay.position_x || 0,
        position_y: overlay.position_y || 0,
        width: overlay.width || 100,
        height: overlay.height || 50,
      });
    }
  }, [overlay]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'overlay_type' ? value : (name.includes('_') || name === 'width' || name === 'height' ? parseFloat(value) || 0 : value),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{overlay ? 'Edit Overlay' : 'Create New Overlay'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="overlay_type">Overlay Type</label>
            <select
              id="overlay_type"
              name="overlay_type"
              value={formData.overlay_type}
              onChange={handleChange}
              required
            >
              <option value="text">Text</option>
              <option value="image">Image (URL)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="content">
              {formData.overlay_type === 'text' ? 'Text Content' : 'Image URL'}
            </label>
            {formData.overlay_type === 'text' ? (
              <textarea
                id="content"
                name="content"
                value={formData.content}
                onChange={handleChange}
                placeholder="Enter text content"
                required
              />
            ) : (
              <input
                type="url"
                id="content"
                name="content"
                value={formData.content}
                onChange={handleChange}
                placeholder="https://example.com/image.png"
                required
              />
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="position_x">Position X</label>
              <input
                type="number"
                id="position_x"
                name="position_x"
                value={formData.position_x}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="position_y">Position Y</label>
              <input
                type="number"
                id="position_y"
                name="position_y"
                value={formData.position_y}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="width">Width</label>
              <input
                type="number"
                id="width"
                name="width"
                value={formData.width}
                onChange={handleChange}
                min="50"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="height">Height</label>
              <input
                type="number"
                id="height"
                name="height"
                value={formData.height}
                onChange={handleChange}
                min="30"
                required
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onCancel} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              {overlay ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OverlayForm;
