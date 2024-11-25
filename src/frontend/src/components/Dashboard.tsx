import React, { useEffect, useState } from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import MetricsChart from './MetricsChart';
import AnomalyAlert from './AnomalyAlert';
import { socket } from '../socket';
import { MetricsData } from '../types';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(2),
  textAlign: 'center',
  color: theme.palette.text.secondary,
}));

const Dashboard: React.FC = () => {
  const [metricsHistory, setMetricsHistory] = useState<MetricsData[]>([]);
  const [currentMetrics, setCurrentMetrics] = useState<MetricsData | null>(null);
  const [anomalyDetected, setAnomalyDetected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    socket.connect();

    // Listen for metrics updates
    socket.on('metrics_update', (data: MetricsData) => {
      setCurrentMetrics(data);
      setMetricsHistory(prev => [...prev, data].slice(-100)); // Keep last 100 points
    });

    // Listen for anomaly alerts
    socket.on('anomaly_alert', (isAnomaly: boolean) => {
      setAnomalyDetected(isAnomaly);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Streaming Performance Monitor
      </Typography>

      {/* Alerts */}
      {anomalyDetected && <AnomalyAlert />}

      {/* Current Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={4}>
          <Item>
            <Typography variant="h6">Latency</Typography>
            <Typography variant="h4">
              {currentMetrics?.latency.toFixed(2)} ms
            </Typography>
          </Item>
        </Grid>
        <Grid item xs={4}>
          <Item>
            <Typography variant="h6">Buffer Events</Typography>
            <Typography variant="h4">
              {currentMetrics?.buffering || 0}
            </Typography>
          </Item>
        </Grid>
        <Grid item xs={4}>
          <Item>
            <Typography variant="h6">Active Users</Typography>
            <Typography variant="h4">
              {currentMetrics?.users || 0}
            </Typography>
          </Item>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Item>
            <MetricsChart data={metricsHistory} />
          </Item>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
