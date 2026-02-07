# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .db import Base, engine, SessionLocal
from .models import Event
from .schemas import EventIn, EventOut
from .security import require_api_key

# Create tables (simple approach; for production consider migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SQLite Ingestion Service",
    version="1.0.0",
    docs_url=None,        # disable Swagger UI in production
    redoc_url=None,
    openapi_url=None,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

# ----------------------------
# CREATE (POST) - store payload
# ----------------------------
@app.post("/v1/events", response_model=EventOut, dependencies=[Depends(require_api_key)])
def create_event(body: EventIn, db: Session = Depends(get_db)):
    """
    Expected body:
    {
      "source": "optional-string",
      "payload": {
        "stid": "...",
        "exnum": "...",
        "table": {...}
      }
    }
    """
    if not isinstance(body.payload, dict):
        raise HTTPException(status_code=400, detail="payload must be a JSON object")

    # Optional: enforce required keys inside payload
    for key in ("stid", "exnum", "table"):
        if key not in body.payload:
            raise HTTPException(status_code=422, detail=f"payload must include '{key}'")

    e = Event(source=body.source, payload=body.payload)
    db.add(e)
    db.commit()
    db.refresh(e)

    return EventOut(
        id=e.id,
        received_at=e.received_at.isoformat(),
        source=e.source,
        payload=e.payload,
    )

# ----------------------------
# READ - list events (paginated)
# ----------------------------
@app.get("/v1/events", response_model=list[EventOut], dependencies=[Depends(require_api_key)])
def list_events(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    rows = (
        db.query(Event)
        .order_by(desc(Event.id))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        EventOut(
            id=e.id,
            received_at=e.received_at.isoformat(),
            source=e.source,
            payload=e.payload,
        )
        for e in rows
    ]

# ---------------------------------------------------------
# READ - get event ONLY if BOTH id and exnum match (required)
# ---------------------------------------------------------
@app.get("/v1/events/{event_id}", response_model=EventOut, dependencies=[Depends(require_api_key)])
def get_event_by_id_and_exnum(
    event_id: int,
    exnum: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    """
    Call example:
      GET /v1/events/12?exnum=EX1

    Returns 404 if:
      - id doesn't exist, OR
      - id exists but payload.exnum doesn't match the provided exnum
    """
    e = db.get(Event, event_id)
    if not e:
        raise HTTPException(status_code=404, detail="Not found")

    p = e.payload or {}
    if not isinstance(p, dict) or p.get("exnum") != exnum:
        # 404 to avoid leaking existence of IDs with different exnum
        raise HTTPException(status_code=404, detail="Not found")

    return EventOut(
        id=e.id,
        received_at=e.received_at.isoformat(),
        source=e.source,
        payload=e.payload,
    )
