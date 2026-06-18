from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    roles: list[str]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LlmSettingsUpsert(BaseModel):
    api_key: str = Field(min_length=8)
    endpoint: str | None = None
    model: str | None = None
    provider: str | None = None


class LlmSettingsRead(BaseModel):
    provider: str
    endpoint: str | None
    model: str | None
    has_api_key: bool
    updated_at: datetime | None = None


class FindingRead(BaseModel):
    id: int
    source: str
    category: str
    severity: str
    resource_address: str | None
    title: str
    description: str
    recommendation: str
    business_impact: str | None = None
    terraform_fix: str | None = None
    confidence: int

    model_config = {"from_attributes": True}


class ReviewRead(BaseModel):
    id: int
    project_id: int
    status: str
    original_filename: str
    created_at: datetime
    completed_at: datetime | None
    error_message: str | None
    inventory: dict[str, Any] | None
    dependency_graph: dict[str, Any] | None
    scorecard: dict[str, Any] | None
    findings: list[FindingRead]


class DashboardSummary(BaseModel):
    total_reviews: int
    average_score: int
    security_average: int
    cost_average: int
    governance_average: int
    operations_average: int
    security_trend: list[dict[str, Any]]
    cost_trend: list[dict[str, Any]]
    recent_reviews: list[dict[str, Any]]


Severity = Literal["critical", "high", "medium", "low", "info"]
