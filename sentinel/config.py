import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SENTINEL AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Server & Ports
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    DASHBOARD_PORT: int = 8501
    
    # Hardware & Performance
    DEVICE: str = "cpu"
    NUM_THREADS: int = 4
    
    # Camera Settings
    CAMERA_INDEX: int = 0
    CAMERA_BACKEND: str = "DSHOW"  # DirectShow on Windows
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    TARGET_FPS: int = 15
    FRAME_SKIP: int = 2
    
    # Vision & Detection
    DETECTOR_TYPE: str = "ssdlite"  # 'ssdlite' or 'haar'
    CONFIDENCE_THRESHOLD: float = 0.40
    NMS_IOU_THRESHOLD: float = 0.45
    
    # Multi-Object Tracking
    TRACKER_MAX_AGE: int = 15
    TRACKER_MIN_HITS: int = 3
    TRACKER_IOU_THRESHOLD: float = 0.3
    
    # Tripwire & Zones
    TRIPWIRE_POSITION: float = 0.50  # vertical fraction (50% of frame height)
    RECONCILIATION_INTERVAL: int = 60  # seconds between drift checks
    
    # Quality & Reliability
    BLUR_THRESHOLD: float = 60.0  # Laplacian variance threshold
    BRIGHTNESS_MIN: float = 30.0  # Grayscale mean minimum
    BRIGHTNESS_MAX: float = 230.0 # Grayscale mean maximum
    
    # Database & Privacy
    DATABASE_URL: str = "sqlite:///./sentinel.db"
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    STORE_RAW_VIDEO: bool = False
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
os.makedirs(settings.DATA_DIR, exist_ok=True)
