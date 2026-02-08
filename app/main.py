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
# READ - get event by stid (user ID) and exnum
# ---------------------------------------------------------
@app.get("/v1/events/{event_id}", response_model=EventOut, dependencies=[Depends(require_api_key)])
def get_event_by_id_and_exnum(
    event_id: str,
    exnum: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    """
    Call example:
      GET /v1/events/student123?exnum=EX1

    Returns the most recent event matching both stid and exnum.
    Returns 404 if no matching event exists.
    """
    # Query for events where payload.stid matches and payload.exnum matches
    events = (
        db.query(Event)
        .order_by(desc(Event.id))
        .all()
    )
    
    for e in events:
        p = e.payload or {}
        if isinstance(p, dict) and p.get("stid") == event_id and p.get("exnum") == exnum:
            return EventOut(
                id=e.id,
                received_at=e.received_at.isoformat(),
                source=e.source,
                payload=e.payload,
            )
    
    # 404 if no matching event found
    raise HTTPException(status_code=404, detail="Not found")
