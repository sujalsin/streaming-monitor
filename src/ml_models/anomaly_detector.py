import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta

class AnomalyDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_data = []
        self.last_training_time = None
        
    def preprocess_data(self, data):
        """Convert metrics data into feature array"""
        features = np.array([[
            d['latency'],
            d['buffering'],
            d['users']
        ] for d in data])
        return self.scaler.fit_transform(features) if not self.is_trained else self.scaler.transform(features)
    
    def train(self, metrics_history):
        """Train the anomaly detection model"""
        if len(metrics_history) < 100:  # Need minimum amount of data
            return False
            
        features = self.preprocess_data(metrics_history)
        self.model.fit(features)
        self.is_trained = True
        self.last_training_time = datetime.now()
        return True
        
    def predict(self, metrics_data):
        """Predict if current metrics are anomalous"""
        if not self.is_trained:
            return False
            
        features = self.preprocess_data([metrics_data])
        prediction = self.model.predict(features)
        return prediction[0] == -1  # -1 indicates anomaly
        
    def should_retrain(self, current_time=None):
        """Check if model should be retrained"""
        if not self.last_training_time:
            return True
            
        current_time = current_time or datetime.now()
        return (current_time - self.last_training_time) > timedelta(hours=1)
        
    def save_model(self, path):
        """Save the trained model"""
        if self.is_trained:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained,
                'last_training_time': self.last_training_time
            }, path)
            
    def load_model(self, path):
        """Load a trained model"""
        try:
            saved_data = joblib.load(path)
            self.model = saved_data['model']
            self.scaler = saved_data['scaler']
            self.is_trained = saved_data['is_trained']
            self.last_training_time = saved_data['last_training_time']
            return True
        except:
            return False
            
class MetricsPredictor:
    def __init__(self):
        self.latency_history = []
        self.buffer_history = []
        self.user_history = []
        
    def update(self, metrics):
        """Update historical data"""
        self.latency_history.append(metrics['latency'])
        self.buffer_history.append(metrics['buffering'])
        self.user_history.append(metrics['users'])
        
        # Keep only recent history
        max_history = 1000
        if len(self.latency_history) > max_history:
            self.latency_history = self.latency_history[-max_history:]
            self.buffer_history = self.buffer_history[-max_history:]
            self.user_history = self.user_history[-max_history:]
            
    def predict_next(self, window_size=60):
        """Predict next metrics using simple moving average"""
        if len(self.latency_history) < window_size:
            return None
            
        return {
            'latency': np.mean(self.latency_history[-window_size:]),
            'buffering': np.mean(self.buffer_history[-window_size:]),
            'users': np.mean(self.user_history[-window_size:])
        }
