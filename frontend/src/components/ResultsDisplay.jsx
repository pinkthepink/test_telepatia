import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Divider,
  Grid,
  Card,
  CardContent,
  Alert
} from '@mui/material';
import {
  ExpandMore,
  RecordVoiceOver,
  LocalHospital,
  Psychology,
  Person,
  Schedule,
  Warning
} from '@mui/icons-material';

const ResultsDisplay = ({ results }) => {
  if (!results) return null;

  const { data } = results;
  const {
    transcription,
    medical_extraction,
    diagnosis_result,
    processing_time,
    timestamp
  } = data;

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Analysis Results
      </Typography>

      {/* Disclaimer */}
      <Alert severity="warning" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Important:</strong> This is a demonstration application. Results are for 
          educational purposes only and should not be used for actual medical diagnosis. 
          Always consult with qualified healthcare professionals.
        </Typography>
      </Alert>

      {/* Processing Info */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" color="text.secondary">
          Processed in {processing_time?.toFixed(2)}s • {new Date(timestamp).toLocaleString()}
        </Typography>
      </Box>

      {/* Transcription Section */}
      {transcription && (
        <Accordion defaultExpanded sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box display="flex" alignItems="center">
              <RecordVoiceOver sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Audio Transcription</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="body1">
                {transcription}
              </Typography>
            </Paper>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Medical Extraction Section */}
      <Accordion defaultExpanded sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box display="flex" alignItems="center">
            <LocalHospital sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Medical Information</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            {/* Patient Information */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Person sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6">Patient Information</Typography>
                  </Box>
                  
                  {medical_extraction?.patient_info ? (
                    <Box>
                      {medical_extraction.patient_info.name && (
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Name:</strong> {medical_extraction.patient_info.name}
                        </Typography>
                      )}
                      
                      {medical_extraction.patient_info.age && (
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Age:</strong> {medical_extraction.patient_info.age} years
                        </Typography>
                      )}
                      
                      {medical_extraction.patient_info.gender && (
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Gender:</strong> {medical_extraction.patient_info.gender}
                        </Typography>
                      )}
                      
                      {medical_extraction.patient_info.identification_number && (
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>ID:</strong> {medical_extraction.patient_info.identification_number}
                        </Typography>
                      )}
                      
                      {!medical_extraction.patient_info.name && 
                       !medical_extraction.patient_info.age && 
                       !medical_extraction.patient_info.gender && (
                        <Typography variant="body2" color="text.secondary">
                          No patient information extracted
                        </Typography>
                      )}
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No patient information available
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Symptoms */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Symptoms
                  </Typography>
                  
                  {medical_extraction?.symptoms && medical_extraction.symptoms.length > 0 ? (
                    <Box>
                      {medical_extraction.symptoms.map((symptom, index) => (
                        <Chip
                          key={index}
                          label={symptom}
                          variant="outlined"
                          size="small"
                          sx={{ m: 0.5 }}
                        />
                      ))}
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No symptoms identified
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Consultation Reason */}
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Consultation Reason
                  </Typography>
                  <Typography variant="body1">
                    {medical_extraction?.consultation_reason || 'Not specified'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Diagnosis Section */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box display="flex" alignItems="center">
            <Psychology sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Medical Analysis</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            {/* Diagnosis */}
            <Grid item xs={12}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom color="primary.main">
                  Diagnosis
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'primary.50' }}>
                  <Typography variant="body1">
                    {diagnosis_result?.diagnosis || 'No diagnosis provided'}
                  </Typography>
                </Paper>
              </Box>
            </Grid>

            {/* Treatment Plan */}
            <Grid item xs={12}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom color="success.main">
                  Treatment Plan
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'success.50' }}>
                  <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
                    {diagnosis_result?.treatment_plan || 'No treatment plan provided'}
                  </Typography>
                </Paper>
              </Box>
            </Grid>

            {/* Recommendations */}
            <Grid item xs={12}>
              <Box>
                <Typography variant="h6" gutterBottom color="info.main">
                  Recommendations
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'info.50' }}>
                  <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
                    {diagnosis_result?.recommendations || 'No recommendations provided'}
                  </Typography>
                </Paper>
              </Box>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

export default ResultsDisplay;