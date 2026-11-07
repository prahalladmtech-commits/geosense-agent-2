
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv

# Load environment variables from .env when available
load_dotenv()


def get_engine():
    """Create a PostgreSQL/PostGIS database engine securely."""

    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    name = os.getenv("DB_NAME", "geosense_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")

    if not password:
        raise ValueError(
            "DB_PASSWORD is not configured. "
            "Set it in your .env file or deployment environment."
        )

    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username=user,
        password=password,
        host=host,
        port=port,
        database=name,
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True,
    )


def test_connection():
    """Test PostgreSQL/PostGIS connectivity."""

    engine = get_engine()

    with engine.connect() as conn:
        result = conn.execute(text("SELECT PostGIS_Version()"))
        print("Connected! PostGIS version:", result.fetchone()[0])

    engine.dispose()


if __name__ == "__main__":
    test_connection()
