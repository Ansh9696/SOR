from collections import deque
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

MAX_EVENTS = 1000


class Severity(str, Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class EventIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    source: str = Field(min_length=1, max_length=100, examples=["endpoint-agent"])
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    severity: Severity = Severity.info
    occurred_at: datetime | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class Event(EventIn):
    id: UUID
    received_at: datetime


app = FastAPI(
    title="SOR API",
    description="A minimal, safe starting point for security event ingestion.",
    version="0.1.0",
)

_events: deque[Event] = deque(maxlen=MAX_EVENTS)
_events_lock = Lock()


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    """Liveness probe: the API process is responding."""
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz() -> dict[str, str]:
    """Readiness probe: the in-memory event store is initialized."""
    return {"status": "ready"}


@app.post("/api/v1/events", response_model=Event, status_code=status.HTTP_201_CREATED, tags=["events"])
def ingest_event(payload: EventIn) -> Event:
    """Accept and validate an event. No automated response action is performed."""
    event = Event(
        **payload.model_dump(),
        id=uuid4(),
        received_at=datetime.now(timezone.utc),
    )
    with _events_lock:
        _events.appendleft(event)
    return event


@app.get("/api/v1/events", response_model=list[Event], tags=["events"])
def list_events(
    severity: Severity | None = None,
    limit: int = Query(default=100, ge=1, le=MAX_EVENTS),
) -> list[Event]:
    """Return the newest in-memory events, optionally filtered by severity."""
    with _events_lock:
        snapshot = list(_events)
    if severity is not None:
        snapshot = [event for event in snapshot if event.severity == severity]
    return snapshot[:limit]


@app.get("/api/v1/events/{event_id}", response_model=Event, tags=["events"])
def get_event(event_id: UUID) -> Event:
    with _events_lock:
        for event in _events:
            if event.id == event_id:
                return event
    raise HTTPException(status_code=404, detail="Event not found")
