import React, { useState, useEffect } from 'react';
import {
  Backdrop,
  Card,
  CardContent,
  Box,
  Typography,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  Button,
  Fade,
  Chip
} from '@mui/material';
import {
  RecordVoiceOver,
  LocalHospital,
  Psychology,
  Cancel
} from '@mui/icons-material';

const ProcessingOverlay = ({ 
  open, 
  onCancel, 
  hasAudioUrl = false 
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [progress, setProgress] = useState(0);

  // Processing steps based on whether it's audio or text
  const steps = hasAudioUrl 
    ? [
        { label: 'Downloading Audio', icon: <RecordVoiceOver />, duration: 5 },
        { label: 'Transcribing Audio', icon: <RecordVoiceOver />, duration: 10 },
        { label: 'Extracting Medical Info', icon: <LocalHospital />, duration: 8 },
        { label: 'Generating Diagnosis', icon: <Psychology />, duration: 12 }
      ]
    : [
        { label: 'Analyzing Text', icon: <LocalHospital />, duration: 8 },
        { label: 'Extracting Medical Info', icon: <LocalHospital />, duration: 10 },
        { label: 'Generating Diagnosis', icon: <Psychology />, duration: 15 }
      ];

  const totalEstimatedTime = steps.reduce((sum, step) => sum + step.duration, 0);

  useEffect(() => {
    if (!open) {
      setActiveStep(0);
      setElapsedTime(0);
      setProgress(0);
      return;
    }

    const timer = setInterval(() => {
      setElapsedTime(prev => {
        const newTime = prev + 1;
        
        // Calculate which step we should be on based on elapsed time
        let accumulatedTime = 0;
        let currentStep = 0;
        
        for (let i = 0; i < steps.length; i++) {
          accumulatedTime += steps[i].duration;
          if (newTime < accumulatedTime) {
            currentStep = i;
            break;
          }
          currentStep = i + 1;
        }
        
        setActiveStep(Math.min(currentStep, steps.length - 1));
        
        // Calculate overall progress
        const progressPercent = Math.min((newTime / totalEstimatedTime) * 100, 95);
        setProgress(progressPercent);
        
        return newTime;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [open, steps.length, totalEstimatedTime]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const estimatedRemaining = Math.max(0, totalEstimatedTime - elapsedTime);

  return (
    <Backdrop
      open={open}
      sx={{ 
        zIndex: 9999, 
        backdropFilter: 'blur(4px)',
        backgroundColor: 'rgba(0, 0, 0, 0.7)'
      }}
    >
      <Fade in={open}>
        <Card 
          sx={{ 
            maxWidth: 600, 
            width: '90%', 
            mx: 2,
            borderRadius: 3,
            boxShadow: 24
          }}
        >
          <CardContent sx={{ p: 4 }}>
            {/* Header */}
            <Box textAlign="center" mb={3}>
              <Box 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  mb: 2,
                  '& svg': {
                    fontSize: 48,
                    color: 'primary.main',
                    animation: 'pulse 2s infinite'
                  }
                }}
              >
                {steps[activeStep]?.icon}
              </Box>
              
              <Typography variant="h5" color="primary" gutterBottom>
                Processing Medical Information
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                AI is analyzing your {hasAudioUrl ? 'audio file' : 'text'} to extract medical insights
              </Typography>
            </Box>

            {/* Progress Bar */}
            <Box mb={3}>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2" color="text.secondary">
                  Overall Progress
                </Typography>
                <Typography variant="body2" color="primary" fontWeight="bold">
                  {Math.round(progress)}%
                </Typography>
              </Box>
              
              <LinearProgress 
                variant="determinate" 
                value={progress} 
                sx={{ 
                  height: 8, 
                  borderRadius: 4,
                  backgroundColor: 'rgba(0,0,0,0.1)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4,
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)'
                  }
                }} 
              />
            </Box>

            {/* Processing Steps */}
            <Box mb={3}>
              <Stepper activeStep={activeStep} orientation="vertical">
                {steps.map((step, index) => (
                  <Step key={step.label}>
                    <StepLabel
                      icon={
                        <Box 
                          sx={{ 
                            display: 'flex', 
                            alignItems: 'center',
                            color: index === activeStep ? 'primary.main' : 
                                   index < activeStep ? 'success.main' : 'text.disabled'
                          }}
                        >
                          {React.cloneElement(step.icon, { fontSize: 'small' })}
                        </Box>
                      }
                    >
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body2">
                          {step.label}
                        </Typography>
                        {index === activeStep && (
                          <Chip 
                            label="In Progress" 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                          />
                        )}
                        {index < activeStep && (
                          <Chip 
                            label="Complete" 
                            size="small" 
                            color="success" 
                            variant="filled"
                          />
                        )}
                      </Box>
                    </StepLabel>
                  </Step>
                ))}
              </Stepper>
            </Box>

            {/* Time Information */}
            <Box 
              display="flex" 
              justifyContent="space-between" 
              alignItems="center"
              sx={{ 
                p: 2, 
                backgroundColor: 'grey.50', 
                borderRadius: 2,
                mb: 2
              }}
            >
              <Box textAlign="center">
                <Typography variant="caption" color="text.secondary">
                  Elapsed Time
                </Typography>
                <Typography variant="h6" color="primary">
                  {formatTime(elapsedTime)}
                </Typography>
              </Box>
              
              <Box textAlign="center">
                <Typography variant="caption" color="text.secondary">
                  Est. Remaining
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  {formatTime(estimatedRemaining)}
                </Typography>
              </Box>
            </Box>

            {/* Current Status */}
            <Box textAlign="center" mb={3}>
              <Typography variant="body2" color="text.secondary">
                {steps[activeStep]?.label}... Please wait while our AI processes your medical information.
              </Typography>
            </Box>

            {/* Cancel Button */}
            {onCancel && (
              <Box textAlign="center">
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<Cancel />}
                  onClick={onCancel}
                  size="small"
                >
                  Cancel Processing
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>
      </Fade>

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes pulse {
          0% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.05); opacity: 0.8; }
          100% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </Backdrop>
  );
};

export default ProcessingOverlay;