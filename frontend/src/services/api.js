import axios from 'axios';
import { authService } from './auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors (unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.clearAuth();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication
export const register = async (username, email, password) => {
  const response = await api.post('/auth/register', { username, email, password });
  return response.data;
};

export const login = async (username, password) => {
  const response = await api.post('/auth/login', { username, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Stream Settings
export const getStreamSettings = async () => {
  const response = await api.get('/stream/settings');
  return response.data;
};

export const updateStreamSettings = async (settings) => {
  const response = await api.post('/stream/settings', settings);
  return response.data;
};

// HLS Stream
export const getHLSStreamUrl = (streamId) => {
  return `${API_BASE_URL}/stream/hls/${streamId}`;
};

export const getStreamStatus = async (streamId) => {
  const response = await api.get(`/stream/status/${streamId}`);
  return response.data;
};

export const stopStream = async (streamId) => {
  const response = await api.post(`/stream/stop/${streamId}`);
  return response.data;
};

// Overlays
export const getOverlays = async () => {
  const response = await api.get('/overlays');
  return response.data;
};

export const getOverlay = async (id) => {
  const response = await api.get(`/overlays/${id}`);
  return response.data;
};

export const createOverlay = async (overlay) => {
  const response = await api.post('/overlays', overlay);
  return response.data;
};

export const updateOverlay = async (id, overlay) => {
  const response = await api.put(`/overlays/${id}`, overlay);
  return response.data;
};

export const deleteOverlay = async (id) => {
  const response = await api.delete(`/overlays/${id}`);
  return response.data;
};
