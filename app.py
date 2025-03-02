from fastapi import FastAPI, Form, Depends, HTTPException, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pathlib import Path
from database import get_db, init_db
from models import User
from pydantic import BaseModel
from utils.audio_handler import recognize_speech_from_audio
from utils.docx_handler import extract_text_from_docx
from utils.pdf_handler import extract_pdf_text

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    return {"message": "Успешный вход"}

# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     file_type = file.filename.split(".")[-1].lower()
#     allowed_extensions = {"pdf", "docx", "wav", "mp3", "ogg"}

#     if file_type not in allowed_extensions:
#         raise HTTPException(status_code=400, detail="Неподдерживаемый формат")

#     if file_type == "pdf":
#         text = extract_pdf_text(file)
#     elif file_type == "docx":
#         text = extract_text_from_docx(file)
#     elif file_type in {"wav", "mp3", "ogg"}:
#         text = recognize_speech_from_audio(file)

#     return {"filename": file.filename, "extracted_text": text}

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
