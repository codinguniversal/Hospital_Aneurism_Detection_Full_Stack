from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    holds default values incase no environmental variables are found
    """
    #Database configuration
    database_mode: str = "mongodb"  # Options: "mock" or "mongodb
    mongodb_uri: str = "mongodb://127.0.0.1:27017"
    mongodb_db_name: str = "CAD_DB"

    # AI
    use_mock_ai: bool = True

    # security configurations
    JWT_SECRET: str= "YOUR_SUPER_SECRET_ENVIRONMENT_KEY_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    # API Versioning
    api_v1_str: str = "/api/v1"

    class Config:
        env_file = ".env"

static_settings = Settings()