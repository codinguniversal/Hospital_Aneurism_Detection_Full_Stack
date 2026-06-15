from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    holds default values incase no environmental variables are found
    """
    ai_api_url: str = "http://127.0.0.1:8000/analyze"
    ai_timeout_limit: int = 60
    automatic_scan_start_hour:  int = 8
    automatic_scan_end_hour: int = 17
    automatic_scan_interval = 60
    class Config:
        env_file = ".env"

settings = Settings()