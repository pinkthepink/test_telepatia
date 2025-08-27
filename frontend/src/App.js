import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Alert,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
  Paper,
  Chip,
  IconButton,
  Snackbar
} from '@mui/material';
import { 
  LocalHospital, 
  Refresh,
  MonitorHeart 
} from '@mui/icons-material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import AudioInput from './components/AudioInput';
import TextInput from './components/TextInput';
import ResultsDisplay from './components/ResultsDisplay';
import ProcessingOverlay from './components/ProcessingOverlay';
import { medicalAPI } from './services/api';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [healthStatus, setHealthStatus] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [currentRequest, setCurrentRequest] = useState(null);

  // Check backend health on component mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const health = await medicalAPI.healthCheck();
      setHealthStatus(health);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus({ status: 'unhealthy', error: error.message });
    }
  };

  const handleSubmit = async (requestData, progressCallback) => {
    setIsProcessing(true);
    setError('');
    setResults(null);
    setCurrentRequest(requestData);

    try {
      let response;
      
      if (requestData.file) {
        // Handle file upload
        response = await medicalAPI.processUpload(requestData.file, progressCallback);
      } else {
        // Handle URL or text processing
        response = await medicalAPI.processRequest(requestData);
      }
      
      setResults(response);
      setSnackbar({
        open: true,
        message: 'Processing completed successfully!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Processing error:', error);
      setError(error.message || 'An error occurred during processing');
      setSnackbar({
        open: true,
        message: 'Processing failed. Please try again.',
        severity: 'error'
      });
    } finally {
      setIsProcessing(false);
      setCurrentRequest(null);
    }
  };

  const handleCancelProcessing = () => {
    // Note: This would require implementing request cancellation in the API
    setIsProcessing(false);
    setCurrentRequest(null);
    setSnackbar({
      open: true,
      message: 'Processing cancelled',
      severity: 'info'
    });
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
    setError('');
    setResults(null);
  };

  const handleRefresh = () => {
    setResults(null);
    setError('');
    checkBackendHealth();
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <LocalHospital sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Medical Information Processing
          </Typography>
          
          {/* Health Status Indicator */}
          <Box display="flex" alignItems="center" gap={1}>
            {healthStatus && (
              <Chip
                icon={<MonitorHeart />}
                label={healthStatus.status === 'healthy' ? 'API Online' : 'API Offline'}
                color={healthStatus.status === 'healthy' ? 'success' : 'error'}
                variant="outlined"
                size="small"
              />
            )}
            
            <IconButton color="inherit" onClick={handleRefresh}>
              <Refresh />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Welcome Section */}
        <Paper elevation={1} sx={{ p: 3, mb: 4, bgcolor: 'primary.50' }}>
          <Typography variant="h4" gutterBottom>
            AI-Powered Medical Analysis
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Upload an audio file or enter text to extract medical information, 
            identify symptoms, and generate diagnostic insights using advanced language models.
          </Typography>
        </Paper>

        {/* Backend Status Alert */}
        {healthStatus && healthStatus.status !== 'healthy' && (
          <Alert severity="error" sx={{ mb: 3 }}>
            Backend API is not available. Please ensure the backend service is running.
          </Alert>
        )}

        {/* Input Tabs */}
        <Paper elevation={2} sx={{ mb: 3 }}>
          <Tabs 
            value={currentTab} 
            onChange={handleTabChange}
            variant="fullWidth"
          >
            <Tab label="Audio Input" />
            <Tab label="Text Input" />
          </Tabs>
        </Paper>

        {/* Tab Content */}
        <Box sx={{ mb: 3 }}>
          {currentTab === 0 && (
            <AudioInput onSubmit={handleSubmit} isProcessing={isProcessing} />
          )}
          {currentTab === 1 && (
            <TextInput onSubmit={handleSubmit} isProcessing={isProcessing} />
          )}
        </Box>

        {/* Processing Overlay */}
        <ProcessingOverlay
          open={isProcessing}
          onCancel={handleCancelProcessing}
          hasAudioUrl={currentRequest?.audio_url || currentRequest?.file ? true : false}
        />

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Results Display */}
        {results && !isProcessing && (
          <ResultsDisplay results={results} />
        )}

        {/* Footer */}
        <Box sx={{ mt: 6, p: 2, textAlign: 'center', color: 'text.secondary' }}>
          <Typography variant="body2">
            Medical Information Processing System • Built with LangGraph & React
          </Typography>
          <Typography variant="caption">
            For demonstration purposes only • Not for actual medical use
          </Typography>
        </Box>
      </Container>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;