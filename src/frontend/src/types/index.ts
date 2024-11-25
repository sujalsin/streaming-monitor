export interface MetricsData {
  timestamp: string;
  latency: number;
  buffering: number;
  users: number;
}

export interface AnomalyData {
  timestamp: string;
  metric: string;
  value: number;
  expected_range: [number, number];
}

export interface PredictionData {
  timestamp: string;
  metric: string;
  predicted_value: number;
  confidence_interval: [number, number];
}
