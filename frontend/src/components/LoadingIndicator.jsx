import React, { useState, useEffect } from 'react';
import { 
  Box, 
  CircularProgress, 
  Typography, 
  LinearProgress,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import { LocalHospital } from '@mui/icons-material';

const LoadingIndicator = ({ 
  message = 'Processing...', 
  variant = 'circular',
  showTimeEstimate = true 
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [dots, setDots] = useState('');

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const dotsTimer = setInterval(() => {
      setDots(prev => {
        if (prev === '...') return '';
        return prev + '.';
      });
    }, 500);

    return () => clearInterval(dotsTimer);
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getEstimatedTime = () => {
    if (elapsedTime < 5) return "Estimated: 15-30 seconds";
    if (elapsedTime < 15) return "Estimated: 10-20 seconds remaining";
    if (elapsedTime < 25) return "Almost done...";
    return "Processing complex medical analysis...";
  };

  return (
    <Card elevation={2} sx={{ maxWidth: 500, mx: 'auto' }}>
      <CardContent>
        <Box 
          display="flex" 
          flexDirection="column" 
          alignItems="center" 
          justifyContent="center" 
          py={2}
        >
          {/* Icon and Progress */}
          <Box position="relative" display="flex" alignItems="center" mb={2}>
            {variant === 'circular' ? (
              <>
                <CircularProgress 
                  size={80} 
                  thickness={3}
                  sx={{ 
                    color: 'primary.main',
                    '& .MuiCircularProgress-circle': {
                      strokeLinecap: 'round',
                    }
                  }} 
                />
                <Box
                  position="absolute"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  width="100%"
                  height="100%"
                >
                  <LocalHospital 
                    sx={{ 
                      fontSize: 32, 
                      color: 'primary.main',
                      animation: 'pulse 2s infinite'
                    }} 
                  />
                </Box>
              </>
            ) : (
              <LinearProgress 
                sx={{ 
                  width: '100%', 
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: 'rgba(0,0,0,0.1)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4,
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)'
                  }
                }} 
              />
            )}
          </Box>
          
          {/* Processing Message */}
          <Typography 
            variant="h6" 
            color="primary" 
            gutterBottom
            sx={{ fontWeight: 500 }}
          >
            {message}{dots}
          </Typography>
          
          {/* Time Information */}
          {showTimeEstimate && (
            <Box textAlign="center" mb={2}>
              <Chip 
                label={`Elapsed: ${formatTime(elapsedTime)}`}
                variant="outlined" 
                size="small" 
                sx={{ mb: 1, mr: 1 }}
              />
              
              <Typography variant="body2" color="text.secondary">
                {getEstimatedTime()}
              </Typography>
            </Box>
          )}
          
          {/* Status Message */}
          <Typography variant="body2" color="text.secondary" textAlign="center">
            AI is analyzing medical information using advanced language models.
            <br />
            Complex cases may take longer to process accurately.
          </Typography>
        </Box>

        {/* CSS for animations */}
        <style jsx>{`
          @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
          }
        `}</style>
      </CardContent>
    </Card>
  );
};

export default LoadingIndicator;