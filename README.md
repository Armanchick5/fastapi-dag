Описание
Сервис управления ориентированным ациклическим графом (DAG) на FastAPI с хранением в PostgreSQL.

Стек технологий
Python 3.11
FastAPI
SQLAlchemy (async)
Alembic
PostgreSQL
Docker, Docker Compose
pytest, httpx

Установка и запуск

Клонирование репозитория
git clone <repo_url>
cd fastapi-dag

Создание файла .env
cp .env.example .env

Запуск сервисов
docker compose up -d --build

Применение миграций
docker compose run --rm web alembic upgrade head

Открытие API-документации
Перейти в браузере на: http://localhost:8080/docs

Локальный запуск без Docker

Установливаем зависимости
python -m venv venv
source venv/bin/activate   # Linux/MacOS
venv/Scripts/activate      # Windows
pip install -r requirements.txt

Применяем миграции
alembic upgrade head

Запускаем приложение
uvicorn app.main:app --reload --port 8080

Тестирование
pytest --cov=app --cov-report=term-missing

Переменные окружения
Все используемые переменные (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT, DATABASE_URL) описаны в файле .env.
