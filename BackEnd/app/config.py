from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    holds default values incase no environmental variables are found
    """
    ai_api_url: str = "http://127.0.0.1:8000/analyze"
    ai_timeout_limit: int = 60

    # automatic analysis
    automatic_scan_start_hour:  int = 8
    automatic_scan_end_hour: int = 17
    automatic_scan_interval: int  = 60
    
    # urgency definition
    aneurysm_high_risk_threshold: float = 0.8
    aneurysm_medium_risk_threshold: float = 0.4

    #Database configuration
    database_mode: str = "mock"  # Options: "mock" or "mongodb
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "CAD_DB"
    class Config:
        env_file = ".env"

settings = Settings()