from dataclasses import dataclass
from datetime import datetime
import random
from typing import List, Dict
import uuid

@dataclass
class StreamContent:
    content_id: str
    title: str
    type: str  # video, audio, live
    bitrate: int  # in kbps
    resolution: str  # for video
    current_viewers: int
    start_time: datetime
    duration: int  # in seconds
    segment_size: int  # in KB
    cdn_region: str

class ContentSimulator:
    def __init__(self):
        self.active_streams: Dict[str, StreamContent] = {}
        self.cdn_regions = ['us-east', 'us-west', 'eu-west', 'ap-east', 'sa-east']
        self.content_types = {
            'video': {
                'bitrates': [500, 1000, 2000, 4000, 8000],  # kbps
                'resolutions': ['480p', '720p', '1080p', '1440p', '4K'],
                'segment_sizes': [128, 256, 512, 1024, 2048]  # KB
            },
            'audio': {
                'bitrates': [96, 128, 192, 320],  # kbps
                'resolutions': ['N/A'],
                'segment_sizes': [32, 64, 96, 128]  # KB
            },
            'live': {
                'bitrates': [1000, 2000, 4000, 8000],  # kbps
                'resolutions': ['720p', '1080p', '1440p', '4K'],
                'segment_sizes': [256, 512, 1024, 2048]  # KB
            }
        }
        
        # Sample content titles
        self.video_titles = [
            "Nature Documentary: Hidden Wonders",
            "Tech Talk: Future of AI",
            "Cooking Masterclass",
            "Space Exploration Series",
            "Historical Chronicles"
        ]
        
        self.audio_titles = [
            "Classical Symphony No. 9",
            "Tech Podcast Episode 42",
            "Audiobook: Science Fiction",
            "Daily News Broadcast",
            "Music Radio Stream"
        ]
        
        self.live_titles = [
            "Live Sports Event",
            "Breaking News Coverage",
            "Live Concert Stream",
            "Gaming Tournament",
            "Live Tech Conference"
        ]

    def generate_stream(self, content_type: str = None) -> StreamContent:
        if not content_type:
            content_type = random.choice(list(self.content_types.keys()))
            
        # Select appropriate title based on content type
        if content_type == 'video':
            title = random.choice(self.video_titles)
        elif content_type == 'audio':
            title = random.choice(self.audio_titles)
        else:  # live
            title = random.choice(self.live_titles)
            
        type_config = self.content_types[content_type]
        
        bitrate = random.choice(type_config['bitrates'])
        resolution = random.choice(type_config['resolutions'])
        segment_size = random.choice(type_config['segment_sizes'])
        
        stream = StreamContent(
            content_id=str(uuid.uuid4()),
            title=title,
            type=content_type,
            bitrate=bitrate,
            resolution=resolution,
            current_viewers=random.randint(10, 10000),
            start_time=datetime.now(),
            duration=random.randint(300, 7200),  # 5 minutes to 2 hours
            segment_size=segment_size,
            cdn_region=random.choice(self.cdn_regions)
        )
        
        self.active_streams[stream.content_id] = stream
        return stream

    def update_stream_metrics(self, stream_id: str) -> None:
        """Update viewer count and other dynamic metrics for a stream"""
        if stream_id in self.active_streams:
            stream = self.active_streams[stream_id]
            # Simulate viewer count changes
            viewer_change = random.randint(-100, 100)
            stream.current_viewers = max(0, stream.current_viewers + viewer_change)

    def get_active_streams(self) -> List[StreamContent]:
        """Return list of all active streams"""
        return list(self.active_streams.values())

    def remove_stream(self, stream_id: str) -> None:
        """Remove a stream from active streams"""
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]

    def get_total_bandwidth(self) -> float:
        """Calculate total bandwidth usage in Mbps"""
        return sum(s.bitrate * s.current_viewers for s in self.active_streams.values()) / 1000.0

    def get_cdn_distribution(self) -> Dict[str, int]:
        """Get distribution of streams across CDN regions"""
        distribution = {}
        for region in self.cdn_regions:
            distribution[region] = len([s for s in self.active_streams.values() if s.cdn_region == region])
        return distribution

    def get_content_type_distribution(self) -> Dict[str, int]:
        """Get distribution of content types"""
        distribution = {}
        for type_ in self.content_types.keys():
            distribution[type_] = len([s for s in self.active_streams.values() if s.type == type_])
        return distribution
