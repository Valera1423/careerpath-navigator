from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CareerPath Navigator API"
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./data/careerpath.db"

    trudvsem_base_url: str = "http://opendata.trudvsem.ru/api/v1"
    trudvsem_timeout: float = 15.0
    trudvsem_retries: int = 2

    hh_access_token: str = ""

    cors_origins: str = "*"

    max_bot_token: str = ""
    max_webhook_secret: str = "change-me"
    allow_insecure_init_data: bool = False

    # Публичный HTTPS-адрес мини-приложения (Web App).
    # Нужен, чтобы inline-кнопки в боте открывали мини-апп.
    webapp_url: str = ""
    webhook_url: str = ""

    admin_secret: str = "change-me-in-production"

    rate_limit_onboarding: str = "10/minute"
    rate_limit_regenerate: str = "5/minute"
    rate_limit_default: str = "120/minute"
    rate_limit_employer: str = "1000/hour"

    cache_ttl_hours: int = 8

    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()