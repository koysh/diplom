from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import openai
import os
from dotenv import load_dotenv
from extensions import db
from config import Config

# Загрузка переменных окружения
load_dotenv()

# Инициализация приложения Flask
app = Flask(__name__)
app.config.from_object(Config)  # Используйте конфигурацию из config.py
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)

from flask_migrate import Migrate

# Инициализация миграций
migrate = Migrate(app, db)
# Импорт моделей
from models import User, Dialog  

# Обработка главной страницы
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Обработка страницы регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Обработка страницы авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return 'Неверный логин или пароль'
    return render_template('login.html')

# Обработка выхода из системы
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
