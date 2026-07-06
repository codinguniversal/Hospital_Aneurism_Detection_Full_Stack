from typing import Self

from pydantic import BaseModel, Field, HttpUrl, model_validator

class SettingsUpdateRequestSchema(BaseModel):
    ai_api_url: HttpUrl
    ai_timeout_limit: int = Field(gt=0)
    automatic_scan_start_hour: int = Field(ge=0, le=23)
    automatic_scan_end_hour: int = Field(ge=0, le=23)
    automatic_scan_interval: int = Field(gt=0)
    aneurysm_high_risk_threshold: float = Field(ge=0, le=1)
    aneurysm_medium_risk_threshold: float = Field(ge=0, le=1)
    
    @model_validator(mode="after")
    def validate_thresholds(self) -> Self:
        if self.aneurysm_high_risk_threshold <= self.aneurysm_medium_risk_threshold:
            raise ValueError("High risk threshold must be greater than medium risk threshold.")
        return self

class SettingsResponseSchema(BaseModel):
    ai_api_url: HttpUrl
    ai_timeout_limit: int
    automatic_scan_start_hour: int
    automatic_scan_end_hour: int
    automatic_scan_interval: int
    aneurysm_high_risk_threshold: float
    aneurysm_medium_risk_threshold: float