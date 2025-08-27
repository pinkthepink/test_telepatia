import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  Chip
} from '@mui/material';
import {
  TextFields,
  Send,
  Clear
} from '@mui/icons-material';

const TextInput = ({ onSubmit, isProcessing }) => {
  const [text, setText] = useState('');
  const [error, setError] = useState('');

  const validateText = (inputText) => {
    if (!inputText || !inputText.trim()) {
      return 'Text input is required';
    }
    
    if (inputText.trim().length < 10) {
      return 'Please provide at least 10 characters of medical text';
    }
    
    if (inputText.length > 10000) {
      return 'Text is too long (maximum 10,000 characters)';
    }
    
    return '';
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const validationError = validateText(text);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError('');
    onSubmit({ text: text.trim() });
  };

  const handleClear = () => {
    setText('');
    setError('');
  };

  const characterCount = text.length;
  const isNearLimit = characterCount > 8000;

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Box display="flex" alignItems="center" mb={2}>
        <TextFields color="primary" sx={{ mr: 1 }} />
        <Typography variant="h6">Text Processing</Typography>
      </Box>

      <Typography variant="body2" color="text.secondary" mb={2}>
        Enter medical text directly for analysis (symptoms, consultation notes, etc.)
      </Typography>

      <Box component="form" onSubmit={handleSubmit}>
        <TextField
          fullWidth
          multiline
          rows={6}
          label="Medical Text"
          placeholder="Enter patient symptoms, consultation notes, or medical information for analysis..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={isProcessing}
          error={!!error}
          helperText={error}
          sx={{ mb: 2 }}
        />

        <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
          <Chip 
            label={`${characterCount}/10,000 characters`}
            color={isNearLimit ? 'warning' : 'default'}
            variant="outlined"
            size="small"
          />
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box display="flex" gap={2}>
          <Button
            type="submit"
            variant="contained"
            disabled={isProcessing || !text.trim() || text.trim().length < 10}
            startIcon={<Send />}
            sx={{ flex: 1 }}
          >
            {isProcessing ? 'Processing...' : 'Process Text'}
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
          <strong>Examples:</strong> Patient symptoms, medical history, consultation notes, 
          or any medical text that needs analysis and diagnosis.
        </Typography>
      </Alert>
    </Paper>
  );
};

export default TextInput;