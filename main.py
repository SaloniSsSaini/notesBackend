from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
from models import Note
from schemas import NoteCreate, NoteUpdate

# ---------------- CONFIG ----------------
RATE_LIMIT = 5
RATE_LIMIT_WINDOW = 60
API_KEY = "secret123"

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clean Advanced Notes API")

# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- AUTH ----------------
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(401, "Invalid API Key")

# ---------------- HELPERS ----------------
def clean_text(text: str) -> str:
    return " ".join(text.strip().split())

# ---------------- RATE LIMIT ----------------
creation_times = []

def check_rate_limit():
    now = datetime.utcnow()
    window = now - timedelta(seconds=RATE_LIMIT_WINDOW)

    global creation_times
    creation_times = [t for t in creation_times if t > window]

    if len(creation_times) >= RATE_LIMIT:
        raise HTTPException(
            429,
            f"Max {RATE_LIMIT} requests per {RATE_LIMIT_WINDOW}s"
        )

    creation_times.append(now)

# ---------------- CACHE ----------------
search_cache = {}

def clear_cache():
    search_cache.clear()

# ---------------- CREATE NOTE (IDEMPOTENT) ----------------
@app.post("/api/v1/notes", dependencies=[Depends(verify_api_key)])
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    check_rate_limit()

    title = clean_text(note.title)
    content = clean_text(note.content)

    if not title or not content:
        raise HTTPException(400, "Title and content required")

    existing = db.query(Note).filter(
        Note.title == title,
        Note.content == content,
        Note.is_deleted == False
    ).first()

    if existing:
        return existing

    new_note = Note(title=title, content=content)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    clear_cache()
    return new_note

# ---------------- GET NOTES (PAGINATION + SORT) ----------------
@app.get("/api/v1/notes", dependencies=[Depends(verify_api_key)])
def get_notes(
    page: int = 1,
    limit: int = 10,
    sort_by: str = "updated_at",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    allowed = {
        "created_at": Note.created_at,
        "updated_at": Note.updated_at,
        "title": Note.title
    }

    if sort_by not in allowed:
        raise HTTPException(400, f"Invalid sort_by. Allowed: {list(allowed)}")

    column = allowed[sort_by]
    sort_exp = column.asc() if order == "asc" else column.desc()

    query = db.query(Note).filter(Note.is_deleted == False)
    total = query.count()

    notes = (
        query.order_by(sort_exp)
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": notes
    }

# ---------------- UPDATE NOTE ----------------
@app.put("/api/v1/notes/{note_id}", dependencies=[Depends(verify_api_key)])
def update_note(note_id: str, note: NoteUpdate, db: Session = Depends(get_db)):
    existing = db.query(Note).filter(
        Note.id == note_id,
        Note.is_deleted == False
    ).first()

    if not existing:
        raise HTTPException(404, "Note not found")

    updated = False

    if note.title:
        t = clean_text(note.title)
        if t != existing.title:
            existing.title = t
            updated = True

    if note.content:
        c = clean_text(note.content)
        if c != existing.content:
            existing.content = c
            updated = True

    if not updated:
        return {"message": "No changes detected"}

    existing.updated_at = datetime.utcnow()
    existing.updated_by = "system"
    db.commit()
    db.refresh(existing)

    clear_cache()
    return existing

# ---------------- SOFT DELETE ----------------
@app.delete("/api/v1/notes/{note_id}", dependencies=[Depends(verify_api_key)])
def delete_note(note_id: str, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(404, "Note not found")

    note.is_deleted = True
    note.updated_at = datetime.utcnow()
    db.commit()

    clear_cache()
    return {"message": "Note soft deleted"}

# ---------------- ADVANCED SEARCH (RANKED + CACHE) ----------------
@app.get("/api/v1/notes/search", dependencies=[Depends(verify_api_key)])
def search_notes(q: str, db: Session = Depends(get_db)):
    q = clean_text(q).lower()
    if not q:
        raise HTTPException(400, "Empty search query")

    if q in search_cache:
        return search_cache[q]

    results = []

    for note in db.query(Note).filter(Note.is_deleted == False):
        score = 0
        if q in note.title.lower():
            score += 3
        if q in note.content.lower():
            score += 2

        if score > 0:
            results.append({"score": score, "note": note})

    results.sort(key=lambda x: x["score"], reverse=True)
    search_cache[q] = results
    return results

# ---------------- STATS ----------------
@app.get("/api/v1/notes/stats", dependencies=[Depends(verify_api_key)])
def note_stats(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()

    return {
        "total_notes": db.query(Note).filter(Note.is_deleted == False).count(),
        "created_today": db.query(Note).filter(
            Note.created_at >= today,
            Note.is_deleted == False
        ).count(),
        "last_updated_note": db.query(Note)
        .order_by(Note.updated_at.desc())
        .first()
        .id
    }
