from pydantic import BaseModel, Field, HttpUrl

class SettingsUpdateRequestSchema(BaseModel):
    ai_api_url: HttpUrl
    ai_timeout_limit: int = Field(gt=0)
    automatic_scan_start_hour: int = Field(ge=0, le=23)
    automatic_scan_end_hour: int = Field(ge=0, le=23)
    automatic_scan_interval: int = Field(gt=0)
    aneurysm_high_risk_threshold: float = Field(ge=0, le=1)
    aneurysm_medium_risk_threshold: float = Field(ge=0, le=1)

class SettingsResponseSchema(BaseModel):
    ai_api_url: HttpUrl
    ai_timeout_limit: int
    automatic_scan_start_hour: int
    automatic_scan_end_hour: int
    automatic_scan_interval: int
    aneurysm_high_risk_threshold: float
    aneurysm_medium_risk_threshold: float