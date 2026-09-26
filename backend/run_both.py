"""Запускает uvicorn и планировщик в одном процессе для Wispbyte."""
import asyncio
import threading
import uvicorn
from app.services.scheduler import start as start_scheduler
from app.main import app

def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=8080)

def run_scheduler():
    start_scheduler()

if __name__ == "__main__":
    # Планировщик — в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    # Основной поток — uvicorn
    run_uvicorn()