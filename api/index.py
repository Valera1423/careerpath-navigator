"""Точка входа для Vercel. Vercel импортирует `app` из этого файла.

Mangum адаптирует ASGI-приложение FastAPI под формат serverless-функции.
"""
from mangum import Mangum

from backend.app.main import app

# Vercel ожидает переменную `app` или `handler`
handler = Mangum(app, lifespan="off")