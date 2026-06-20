from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    holds default values incase no environmental variables are found
    """
    #Database configuration
    database_mode: str = "mock"  # Options: "mock" or "mongodb
    mongodb_uri: str = "mongodb://127.0.0.1:27017"
    mongodb_db_name: str = "CAD_DB"

    # AI
    use_mock_ai: bool = True
    
    class Config:
        env_file = ".env"

static_settings = Settings()