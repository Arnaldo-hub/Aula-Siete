from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Por defecto SQLite (cero instalación). Para PostgreSQL:
    # DATABASE_URL=postgresql://aulasite:clave@localhost:5432/aulasite
    database_url: str = "sqlite:///./aulasite.db"
    secret_key: str = "dev-secret-cambia-en-produccion"
    access_token_expire_minutes: int = 480
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    class Config:
        env_file = ".env"

    @property
    def db_url(self) -> str:
        # Render entrega 'postgres://'; SQLAlchemy necesita declarar el driver
        # psycopg (v3) explícitamente, si no busca psycopg2 y falla.
        url = self.database_url
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://"):]
        if url.startswith("postgresql://"):
            return "postgresql+psycopg://" + url[len("postgresql://"):]
        return url

settings = Settings()