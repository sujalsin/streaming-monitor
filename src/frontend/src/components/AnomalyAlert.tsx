import React from 'react';
import { Alert, AlertTitle } from '@mui/material';

const AnomalyAlert: React.FC = () => {
  return (
    <Alert severity="warning" sx={{ mb: 2 }}>
      <AlertTitle>Performance Anomaly Detected</AlertTitle>
      Unusual patterns detected in the streaming metrics. Please check the system performance.
    </Alert>
  );
};

export default AnomalyAlert;
