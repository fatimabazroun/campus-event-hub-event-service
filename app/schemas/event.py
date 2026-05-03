from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.models.event import EventStatus


class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    location: str = Field(..., min_length=1, max_length=500)
    start_time: datetime
    end_time: datetime
    capacity: int = Field(..., gt=0)
    organizer_id: str = Field(..., min_length=1, max_length=255)

    @model_validator(mode="after")
    def end_after_start(self) -> "EventCreate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = Field(None, min_length=1, max_length=500)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = Field(None, gt=0)
    status: Optional[EventStatus] = None


class EventResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    location: str
    start_time: datetime
    end_time: datetime
    capacity: int
    organizer_id: str
    status: EventStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    items: list[EventResponse]
    total: int
    page: int
    page_size: int
