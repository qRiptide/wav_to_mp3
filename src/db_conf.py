import os

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn

load_dotenv()


class Settings(BaseSettings):
    asyncpg_url: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_DB_HOST"),
        port=os.getenv("PG_DB_PORT"),
        path=f"/{os.getenv('PG_DB') or ''}"
    )


settings = Settings()
