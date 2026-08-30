from pydantic import BaseModel
from datetime import date
from typing import Optional

class Plan(BaseModel):
    plan_id: int
    plan_name: str
    monthly_price: float

class User(BaseModel):
    user_id: int
    email: str
    signup_date: date
    country: str

class SubscriptionEvent(BaseModel):
    subscription_id: int
    user_id: int
    plan_id: int
    status: str
    start_date: date
    end_date: Optional[date]
    event_type: str
    event_date: date