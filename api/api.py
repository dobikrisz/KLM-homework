from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Note, NoteType

description = """
This API manages a simple note taking application.

With it, cou can create, delete and view notes.
"""

app = FastAPI( title="KLM Homework",
    description=description,
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
    },)

@app.middleware("http")
async def enforce_json(request: Request, call_next):
    if request.method in ("POST", "PUT"):
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            return JSONResponse(status_code=415, content={"detail": "Only application/json requests are accepted"})
    response = await call_next(request)
    return response

@app.middleware("http")
async def enforce_methods(request: Request, call_next):
    if request.method not in ("GET", "POST", "PUT", "DELETE"):
        return JSONResponse(status_code=405, content={"detail": f"Method {request.method} not allowed"})
    response = await call_next(request)
    return response

@app.get("/")
def read_root():
    return "This is the application backend."

@app.get("/notes")
def get_notes_all(db: Session = Depends(get_db)):
    notes = db.query(Note).all()
    return notes

@app.get("/notes/{id}")
def read_note(id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.post("/notes")
def create_note(createdNote: NoteType, db: Session = Depends(get_db)):
    note = Note(
        title=createdNote.title,
        content=createdNote.content,
        creator=createdNote.creator
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@app.put("/notes/{id}")
def update_note(id: int, updatedNote: NoteType, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = updatedNote.title
    note.content = updatedNote.content
    note.creator = updatedNote.creator
    db.commit()
    db.refresh(note)
    return {"message": f"Note: {note.title} was successfully updated (id: {note.id})"}
    
@app.delete("/notes/{id}")
def delete_note(id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"message": f"Note: {note.title} was successfully deleted (id: {note.id})"}
