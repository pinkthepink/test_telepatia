import React, { useState, useRef } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  InputAdornment,
  Tabs,
  Tab,
  LinearProgress,
  Chip
} from '@mui/material';
import {
  AudioFile,
  Send,
  Clear,
  CloudUpload,
  Link
} from '@mui/icons-material';

const AudioInput = ({ onSubmit, isProcessing }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [audioUrl, setAudioUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const validateUrl = (url) => {
    if (!url) return 'Audio URL is required';
    
    try {
      new URL(url);
    } catch {
      return 'Please enter a valid URL';
    }

    // Check for common audio file extensions
    const audioExtensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'];
    const hasAudioExt = audioExtensions.some(ext => 
      url.toLowerCase().includes(ext)
    );
    
    if (!hasAudioExt) {
      return 'URL should point to an audio file (mp3, wav, m4a, etc.)';
    }

    return '';
  };

  const validateFile = (file) => {
    const maxSize = 25 * 1024 * 1024; // 25MB
    const allowedTypes = [
      'audio/mpeg', 'audio/mp3',
      'audio/wav', 'audio/wave',
      'audio/mp4', 'audio/m4a',
      'audio/aac', 'audio/ogg',
      'audio/flac'
    ];
    const allowedExtensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.mp4'];

    if (file.size > maxSize) {
      return `File too large. Maximum size is 25MB. Your file is ${(file.size / (1024 * 1024)).toFixed(1)}MB`;
    }

    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExt)) {
      return 'Unsupported file type. Please select an audio file (MP3, WAV, M4A, AAC, OGG, FLAC)';
    }

    return '';
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setSelectedFile(file);
    setError('');
    setUploadProgress(0);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (!file) return;

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setSelectedFile(file);
    setError('');
    setUploadProgress(0);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (activeTab === 0) {
      // URL tab
      const validationError = validateUrl(audioUrl);
      if (validationError) {
        setError(validationError);
        return;
      }
      setError('');
      onSubmit({ audio_url: audioUrl });
    } else {
      // File upload tab
      if (!selectedFile) {
        setError('Please select an audio file');
        return;
      }
      setError('');
      onSubmit({ file: selectedFile }, (progress) => {
        setUploadProgress(progress);
      });
    }
  };

  const handleClear = () => {
    setAudioUrl('');
    setSelectedFile(null);
    setError('');
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setError('');
    if (newValue === 0) {
      setSelectedFile(null);
      setUploadProgress(0);
    } else {
      setAudioUrl('');
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Box display="flex" alignItems="center" mb={2}>
        <AudioFile color="primary" sx={{ mr: 1 }} />
        <Typography variant="h6">Audio Processing</Typography>
      </Box>

      <Typography variant="body2" color="text.secondary" mb={2}>
        Provide audio for transcription and medical analysis
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab icon={<Link />} label="Audio URL" />
        <Tab icon={<CloudUpload />} label="Upload File" />
      </Tabs>

      <Box component="form" onSubmit={handleSubmit}>
        {activeTab === 0 ? (
          // URL Input Tab
          <TextField
            fullWidth
            label="Audio File URL"
            placeholder="https://example.com/audio-file.mp3"
            value={audioUrl}
            onChange={(e) => setAudioUrl(e.target.value)}
            disabled={isProcessing}
            error={!!error}
            helperText={error || 'Enter a direct link to an audio file'}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <AudioFile />
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
          />
        ) : (
          // File Upload Tab
          <Box>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept="audio/*,.mp3,.wav,.m4a,.aac,.ogg,.flac"
              style={{ display: 'none' }}
            />
            
            <Box
              onClick={() => !isProcessing && fileInputRef.current.click()}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              sx={{
                border: '2px dashed',
                borderColor: error ? 'error.main' : selectedFile ? 'success.main' : 'grey.300',
                borderRadius: 2,
                p: 3,
                mb: 2,
                textAlign: 'center',
                cursor: isProcessing ? 'not-allowed' : 'pointer',
                backgroundColor: selectedFile ? 'success.50' : 'grey.50',
                '&:hover': {
                  backgroundColor: isProcessing ? 'grey.50' : selectedFile ? 'success.100' : 'grey.100',
                }
              }}
            >
              <CloudUpload color={selectedFile ? 'success' : 'action'} sx={{ fontSize: 48, mb: 1 }} />
              <Typography variant="h6" gutterBottom>
                {selectedFile ? selectedFile.name : 'Click to select or drag & drop audio file'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedFile 
                  ? `Size: ${(selectedFile.size / (1024 * 1024)).toFixed(1)}MB`
                  : 'Maximum file size: 25MB'
                }
              </Typography>
              {selectedFile && (
                <Chip
                  label={selectedFile.type || 'Audio file'}
                  color="success"
                  size="small"
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
            
            {uploadProgress > 0 && uploadProgress < 100 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Uploading... {uploadProgress}%
                </Typography>
                <LinearProgress variant="determinate" value={uploadProgress} />
              </Box>
            )}
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box display="flex" gap={2}>
          <Button
            type="submit"
            variant="contained"
            disabled={isProcessing || (activeTab === 0 ? !audioUrl.trim() : !selectedFile)}
            startIcon={activeTab === 0 ? <Send /> : <CloudUpload />}
            sx={{ flex: 1 }}
          >
            {isProcessing ? 'Processing...' : activeTab === 0 ? 'Process URL' : 'Upload & Process'}
          </Button>
          
          <Button
            variant="outlined"
            onClick={handleClear}
            disabled={isProcessing}
            startIcon={<Clear />}
          >
            Clear
          </Button>
        </Box>
      </Box>

      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          <strong>Supported formats:</strong> MP3, WAV, M4A, AAC, OGG, FLAC (max 25MB)
        </Typography>
      </Alert>
    </Paper>
  );
};

export default AudioInput;