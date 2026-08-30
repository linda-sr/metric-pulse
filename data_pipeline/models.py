from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional


class ExtractedSubscriptionEvent(BaseModel):
    subscription_id: int
    user_id: int
    plan_id: int
    status: str
    start_date: date
    end_date: Optional[date] = None
    event_type: str
    event_date: date

    @field_validator("status", "event_type")
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("field cannot be empty")
        return v.strip().lower()


class ExtractedUser(BaseModel):
    user_id: int
    email: str
    signup_date: date
    country: str


class ExtractedPlan(BaseModel):
    plan_id: int
    plan_name: str
    monthly_price: float


class ExtractedClickstreamEvent(BaseModel):
    event_id: str
    user_id: int
    session_id: str
    event_type: str
    page: Optional[str] = None
    feature_name: Optional[str] = None
    timestamp: datetime

    @field_validator("event_type")
    @classmethod
    def valid_event_type(cls, v):
        allowed = {"page_view", "feature_click", "session_start"}
        if v not in allowed:
            raise ValueError(f"unexpected event_type: {v}")
        return v