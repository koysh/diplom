from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import openai
from dotenv import load_dotenv
from utils.docx_handler import extract_text_from_docx
from utils.pdf_handler import extract_text_from_pdf
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Настройка базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель пользователя
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Пароль хранится без хэширования

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройки шаблонов
templates = Jinja2Templates(directory="templates")

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Функция подключения к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Регистрация пользователя (БЕЗ ХЭШИРОВАНИЯ)
@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    new_user = User(username=username, password=password)  # Сохраняем пароль в чистом виде
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/login", status_code=302)

# Авторизация пользователя (БЕЗ ХЭШИРОВАНИЯ)
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/login")
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Чтение содержимого файла
        file_bytes = await file.read()
        logger.info(f"Получен файл: {file.filename}, размер: {len(file_bytes)} байт")

        # Извлечение текста в зависимости от типа файла
        if file.filename.endswith(".docx"):
            extracted_text = extract_text_from_docx(file_bytes)
        elif file.filename.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(file_bytes)
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла (только DOCX и PDF)")

        # Проверка, был ли извлечен текст
        if not extracted_text or "Ошибка" in extracted_text:
            logger.error(f"Не удалось извлечь текст из файла: {file.filename}")
            raise HTTPException(status_code=400, detail="Не удалось извлечь текст из файла")

        # Логируем извлеченный текст
        logger.info(f"Извлеченный текст: {extracted_text}")

        # Отправка текста в OpenAI для анализа
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Пожалуйста, учитывай, что содержимое файла было загружено и доступно для обсуждения."},
                {"role": "user", "content": f"Сделай резюме: {extracted_text}"}
            ]
        )

        # Получаем анализ
        analysis = response.choices[0].message.content

        return {"analysis": analysis, "extracted_text": extracted_text}  # Возвращаем анализ и извлеченный текст
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Произошла ошибка при обработке файла")

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    messages = data.get("messages", [])

    # Логируем полученные сообщения
    logger.info(f"Полученные сообщения: {messages}")

    try:
        # Отправка сообщений в OpenAI для получения ответа
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Получаем ответ от ИИ
        ai_message = response.choices[0].message.content
        return {"response": ai_message}
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)