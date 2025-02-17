from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pdfminer.high_level import extract_text
from docx import Document
import os
import openai
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()  # Загрузка переменных окружения из .env файла

# Получаем API-ключ из переменной окружения
openai.api_key = os.getenv("OPENAI_API_KEY")

# Настройка соединения с базой данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание базы данных
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

# Создание всех таблиц базы данных
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройка Jinja2
templates = Jinja2Templates(directory="templates")

# Настройка статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Функция для работы с базой данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создание папки для загрузок, если она не существует
if not os.path.exists('uploads'):
    os.makedirs('uploads')

def extract_pdf_text(file_path: str) -> str:
    return extract_text(file_path)

def extract_docx_text(file_path: str) -> str:
    doc = Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
    if user is None or password != user.password:
        raise HTTPException(status_code=401, detail="Неверные имя пользователя или пароль")
    
    # Успешный вход
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/login")
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/register", response_class=templates.TemplateResponse, name="register")  
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", name="register")  
async def post_register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
    if user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    new_user = User(username=username, password=password)
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/login", status_code=302)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Проверка на тип файла
    if file.content_type == "application/pdf":
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())
        text = extract_pdf_text(file_location)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())
        text = extract_docx_text(file_location)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Удаляем загруженный файл после обработки
    os.remove(file_location)

    return {"text": text}

@app.post("/ask")
async def ask(request: Request, question: str = Form(...)):
    try:
        print(f"Вопрос от пользователя: {question}")

        # Проверка на наличие API-ключа
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="API ключ не найден")

        # Запрос к OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": question}
            ]
        )

        # Извлечение ответа
        answer = response.choices[0].message['content']

        print(f"Ответ ИИ: {answer}")
        return {"response": answer}

    except Exception as e:
        print(f"Ошибка при обращении к ИИ: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к ИИ: {str(e)}")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
