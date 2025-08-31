"""
Main module for API hosting
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# pylint: disable=import-error
from api.database import get_db, engine

# pylint: disable=import-error
from api.models import Note, NoteType, Base

DESCRIPTION = """
This API manages a simple note taking application.

With it, you can create, delete and view notes.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup code, if any


app = FastAPI(
    lifespan=lifespan,
    title="KLM Homework",
    description=DESCRIPTION,
    summary="Note taking app API",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Krisztian Dobos",
        "email": "dobikrsz@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


@app.middleware("http")
async def enforce_json(request: Request, call_next):
    """
    enforcing json body type for POST and PUT requests
    """
    if request.method in ("POST", "PUT"):
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            return JSONResponse(
                status_code=415,
                content={"detail": "Only application/json requests are accepted"},
            )
    response = await call_next(request)
    return response


@app.middleware("http")
async def enforce_methods(request: Request, call_next):
    """
    enforcing accepted methods GET, POST, PUT, DELETE
    """
    if request.method not in ("GET", "POST", "PUT", "DELETE"):
        return JSONResponse(
            status_code=405, content={"detail": f"Method {request.method} not allowed"}
        )
    response = await call_next(request)
    return response


@app.get("/")
def read_root():
    """
    return for root request
    """
    return "This is the application backend."


@app.get("/notes")
def get_notes_all(db: Session = Depends(get_db)):
    """
    returns all notes
    """
    notes = db.query(Note).all()
    return notes


@app.get("/notes/{note_id}")
def read_note(note_id: int, db: Session = Depends(get_db)):
    """
    returns note by id
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.post("/notes")
def create_note(created_note: NoteType, db: Session = Depends(get_db)):
    """
    inserts new note into db
    """
    note = Note(
        title=created_note.title,
        content=created_note.content,
        creator=created_note.creator,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.put("/notes/{note_id}")
def update_note(note_id: int, updated_note: NoteType, db: Session = Depends(get_db)):
    """
    updates existing note
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = updated_note.title
    note.content = updated_note.content
    note.creator = updated_note.creator
    db.commit()
    db.refresh(note)
    return {"message": f"Note: {note.title} was successfully updated (id: {note.id})"}


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """
    deletes note from db
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"message": f"Note: {note.title} was successfully deleted (id: {note.id})"}
