from typing import Self

from pydantic import BaseModel, Field, HttpUrl, model_validator


class SettingsEntity(BaseModel):
    ai_api_url: HttpUrl
    ai_timeout_limit: int = Field(gt=0, description="AI timeout limit must be a positive integer.")
    automatic_scan_start_hour: int = Field(ge=0, le=23, description="Start hour must be between 0 and 23.")
    automatic_scan_end_hour: int = Field(ge=0, le=23, description="End hour must be between 0 and 23.")
    automatic_scan_interval: int = Field(gt=0, description="Scan interval must be a positive integer.")
    aneurysm_high_risk_threshold: float = Field(gt=0, lt=1, description="High risk threshold must be between 0 and 1.")
    aneurysm_medium_risk_threshold: float = Field(gt=0, lt=1, description="Medium risk threshold must be between 0 and 1.")

    @model_validator(mode="after")
    def validate_business_invariants(self) -> Self:
        if self.aneurysm_high_risk_threshold <= self.aneurysm_medium_risk_threshold:
            raise ValueError("High risk threshold must be greater than medium risk threshold.")
        if self.automatic_scan_start_hour >= self.automatic_scan_end_hour:
            raise ValueError("Start hour must be less than end hour.")
        return self
