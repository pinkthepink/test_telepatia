import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 180000, // 180 second timeout for processing (3 minutes)
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    if (error.response?.status === 500) {
      throw new Error('Server error occurred. Please try again later.');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail?.message || 'Invalid request data');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. Please try again.');
    } else {
      throw new Error(error.response?.data?.detail || error.message || 'An error occurred');
    }
  }
);

export const medicalAPI = {
  // Process medical request (audio URL or text)
  processRequest: async (data) => {
    const response = await api.post('/process', data);
    return response.data;
  },

  // Process uploaded file
  processUpload: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/process/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        if (onProgress) {
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get metrics
  getMetrics: async () => {
    const response = await api.get('/metrics');
    return response.data;
  },

  // Get workflow status
  getWorkflowStatus: async () => {
    const response = await api.get('/workflow/status');
    return response.data;
  }
};

export default api;