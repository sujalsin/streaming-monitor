from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import socketio
import redis
import json
import asyncio
from datetime import datetime
import numpy as np
from prometheus_client import Counter, Histogram, start_http_server
import random
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize FastAPI app
app = FastAPI(title="Streaming Performance Monitor")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
def get_redis_client():
    try:
        client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        client.ping()  # Test the connection
        return client
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

# Initialize Redis client
try:
    redis_client = get_redis_client()
    logger.info("Successfully connected to Redis")
except Exception as e:
    logger.error(f"Failed to initialize Redis client: {e}")
    raise

# Initialize metrics
request_count = Counter('request_count', 'Number of requests processed')
latency_histogram = Histogram('request_latency_seconds', 'Request latency in seconds')

# Initialize Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=['*'])
socket_app = socketio.ASGIApp(sio)
app.mount("/ws", socket_app)

from .content_simulator import ContentSimulator

# Initialize content simulator
content_simulator = ContentSimulator()

# Create initial streams
for _ in range(5):
    content_simulator.generate_stream()

class StreamingMetrics:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.buffer_count = 0
        self.total_latency = 0
        self.user_count = 0
        self.metrics_history = []

    def update_metrics(self, latency, buffering, users):
        self.total_latency += latency
        self.buffer_count += buffering
        self.user_count = users
        
        # Create metrics data
        metric_data = {
            'timestamp': datetime.now().isoformat(),
            'latency': latency,
            'buffering': buffering,
            'users': users
        }
        
        # Store metrics history in memory
        self.metrics_history.append(metric_data)
        
        # Keep only last 1000 metrics in memory
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)
        
        # Store in Redis
        try:
            self.redis_client.lpush('metrics_history', json.dumps(metric_data))
            # Keep only last 1000 metrics in Redis
            self.redis_client.ltrim('metrics_history', 0, 999)
        except Exception as e:
            print(f"Error storing metrics in Redis: {e}")

metrics = StreamingMetrics(redis_client)

async def store_metrics(metrics):
    try:
        await sio.emit('metrics_update', metrics)
        redis_client.lpush('metrics_history', json.dumps(metrics))
        redis_client.ltrim('metrics_history', 0, 999)
    except Exception as e:
        logger.error(f"Error storing metrics: {e}")

async def generate_metrics():
    """Generate random metrics data"""
    while True:
        # Update existing stream metrics
        for stream in content_simulator.get_active_streams():
            content_simulator.update_stream_metrics(stream.content_id)
            
        # Randomly add or remove streams
        if random.random() < 0.1:  # 10% chance to add a new stream
            content_simulator.generate_stream()
        if random.random() < 0.05:  # 5% chance to remove a stream
            active_streams = content_simulator.get_active_streams()
            if active_streams:
                content_simulator.remove_stream(random.choice(active_streams).content_id)

        # Generate basic metrics
        timestamp = datetime.now().isoformat()
        latency = random.gauss(100, 20)  # Mean of 100ms, std dev of 20ms
        buffering = random.poisson(5)  # Poisson distribution with mean of 5
        users = int(random.gauss(1000, 200))  # Mean of 1000 users, std dev of 200

        # Add streaming-specific metrics
        metrics = {
            "timestamp": timestamp,
            "latency": latency,
            "buffering": buffering,
            "users": users,
            "total_bandwidth_mbps": content_simulator.get_total_bandwidth(),
            "active_streams": len(content_simulator.get_active_streams()),
            "cdn_distribution": content_simulator.get_cdn_distribution(),
            "content_types": content_simulator.get_content_type_distribution()
        }

        # Store in Redis
        try:
            await store_metrics(metrics)
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")

        await asyncio.sleep(1)

@app.get("/")
async def root():
    return {"message": "Streaming Performance Monitor API"}

@app.get("/metrics")
async def get_metrics():
    try:
        # Get metrics from Redis
        redis_metrics = redis_client.lrange('metrics_history', 0, 99)  # Get last 100 metrics
        history = [json.loads(m) for m in redis_metrics]
    except Exception as e:
        print(f"Error retrieving metrics from Redis: {e}")
        history = metrics.metrics_history[-100:]  # Fallback to in-memory metrics
    
    return {
        "current_metrics": {
            "latency": metrics.total_latency / max(1, len(metrics.metrics_history)),
            "buffer_count": metrics.buffer_count,
            "user_count": metrics.user_count
        },
        "history": history
    }

@sio.on('connect')
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    # Send initial metrics
    if metrics.metrics_history:
        await sio.emit('metrics_update', metrics.metrics_history[-1], room=sid)

@sio.on('disconnect')
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.on('metric_update')
async def handle_metric_update(sid, data):
    # Process incoming metrics
    metrics.update_metrics(
        latency=data.get('latency', 0),
        buffering=data.get('buffering', 0),
        users=data.get('users', 0)
    )
    
    # Broadcast updated metrics to all clients
    await sio.emit('metrics_update', metrics.metrics_history[-1])

@app.on_event("startup")
async def startup_event():
    try:
        # Clear existing metrics
        redis_client.delete('metrics_history')
        
        # Start Prometheus metrics server
        start_http_server(9090)
        
        # Start metrics simulation
        asyncio.create_task(generate_metrics())
        print("Application startup complete")
    except Exception as e:
        print(f"Error during startup: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
