import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.models.event import Event
from app.schemas.event import (
    EventCreate,
    EventListResponse,
    EventResponse,
    EventUpdate,
)

router = APIRouter(tags=["events"])
logger = logging.getLogger(__name__)

_WRITE_DEPS = [Depends(verify_api_key)]


@router.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=_WRITE_DEPS,
)
async def create_event(payload: EventCreate, db: AsyncSession = Depends(get_db)):
    event = Event(**payload.model_dump())
    db.add(event)
    await db.commit()
    await db.refresh(event)
    logger.info("Event created", extra={"event_id": event.id})
    return event


@router.get("/events", response_model=EventListResponse)
async def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    total = (await db.execute(select(func.count()).select_from(Event))).scalar_one()
    rows = (
        await db.execute(
            select(Event).order_by(Event.created_at.desc()).offset(offset).limit(page_size)
        )
    ).scalars().all()
    return EventListResponse(items=rows, total=total, page=page, page_size=page_size)


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    event = (
        await db.execute(select(Event).where(Event.id == event_id))
    ).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.put(
    "/events/{event_id}",
    response_model=EventResponse,
    dependencies=_WRITE_DEPS,
)
async def update_event(
    event_id: str, payload: EventUpdate, db: AsyncSession = Depends(get_db)
):
    event = (
        await db.execute(select(Event).where(Event.id == event_id))
    ).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    await db.commit()
    await db.refresh(event)
    logger.info("Event updated", extra={"event_id": event_id})
    return event


@router.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=_WRITE_DEPS,
)
async def delete_event(event_id: str, db: AsyncSession = Depends(get_db)):
    event = (
        await db.execute(select(Event).where(Event.id == event_id))
    ).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    await db.delete(event)
    await db.commit()
    logger.info("Event deleted", extra={"event_id": event_id})
