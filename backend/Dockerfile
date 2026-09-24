FROM python:3.12-slim

# Системные CA. Русский корневой сертификат (Минцифры) копируется
# из контекста сборки — надёжнее, чем качать через curl: gu-st.ru
# часто недоступен из РФ-сетей и отдаёт HTML вместо PEM.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Русский CA — чтобы httpx доверял platform-api2.max.ru.
# Наш SSL-контекст в max_api.py загружает его напрямую,
# но положим и в системный store для остальных клиентов.
COPY russiantrustedca.pem /usr/local/share/ca-certificates/russian-trusted-ca.crt
RUN update-ca-certificates

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini entrypoint.sh ./
COPY alembic ./alembic
COPY app ./app

RUN chmod +x entrypoint.sh \
    && mkdir -p /app/data

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]