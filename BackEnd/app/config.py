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

    # security configurations
    JWT_SECRET: str= "YOUR_SUPER_SECRET_ENVIRONMENT_KEY_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    # API Versioning
    api_v1_str: str = "/api/v1"

    #local host storage directory for AI medical images
    storage_base_dir: str = "app/infrastructure/storage/scan_slices"
    slice_meta_collection_name: str = "slice_metadata"

    # notifications 
    notification_provider_class: str = "app.infrastructure.notifications.mail_trap_notifier.MailtrapEmailNotifier"

    #mailtrap sandbox credentials
    mailtrap_api_token: str = "976ad151ea2ee1f78c091c16e970c43a"
    mailtrap_inbox_id: str = "4741204"
    notification_recipients: str = "20220833@stud.fci-cu.edu.eg"
    sender_email: str = "alerts@test.com"

    class Config:
        env_file = ".env"

static_settings = Settings()