"""Casa Biônica — Configuração centralizada via env vars."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/casa_bionica"

    # MQTT
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_topic_prefix: str = "casa_bionica"

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    home_id: str = "home-001"

    # Supabase
    supabase_jwt_secret: str = ""


settings = Settings()
