
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"

# Load project environment variables without overwriting
# environment variables already supplied by the host.
load_dotenv(
    dotenv_path=ENV_FILE,
    override=False
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

def get_engine():
    """
    Create and return a PostgreSQL database engine.

    Supports:
        1. DATABASE_URL
        2. Individual DB_HOST, DB_PORT, DB_NAME,
           DB_USER and DB_PASSWORD variables.

    Credentials must be supplied through environment
    variables or the local .env file.
    """

    database_url = os.getenv("DATABASE_URL")

    # --------------------------------------------------------
    # OPTION 1: DATABASE_URL
    # --------------------------------------------------------

    if database_url:

        try:
            database_url = database_url.strip()

            # Some hosting providers use postgres://.
            # SQLAlchemy expects postgresql://.
            if database_url.startswith("postgres://"):
                database_url = database_url.replace(
                    "postgres://",
                    "postgresql://",
                    1
                )

            url = make_url(database_url)

            # Ensure psycopg2 is used.
            if url.drivername == "postgresql":
                url = url.set(
                    drivername="postgresql+psycopg2"
                )

            sslmode = os.getenv("DB_SSLMODE")

            if sslmode:
                url = url.update_query_dict({
                    "sslmode": sslmode
                })

            return create_engine(
                url,
                pool_pre_ping=True,
                pool_recycle=1800,
                connect_args={
                    "connect_timeout": 10
                }
            )

        except Exception as error:
            raise RuntimeError(
                "Invalid DATABASE_URL configuration."
            ) from error

    # --------------------------------------------------------
    # OPTION 2: INDIVIDUAL DATABASE VARIABLES
    # --------------------------------------------------------

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "geosense_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")

    if not password:
        raise RuntimeError(
            "Database password is missing. "
            "Configure DB_PASSWORD or DATABASE_URL."
        )

    sslmode = os.getenv("DB_SSLMODE")

    query = {}

    if sslmode:
        query["sslmode"] = sslmode

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=user,
        password=password,
        host=host,
        port=int(port),
        database=name,
        query=query
    )

    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={
            "connect_timeout": 10
        }
    )


# ============================================================
# DATABASE CONNECTION TEST
# ============================================================

def test_connection():
    """
    Test the PostgreSQL and PostGIS connection.
    """

    engine = get_engine()

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT PostGIS_Version()")
            )

            version = result.scalar()

            print("Database connection successful!")
            print("PostGIS version:", version)

            return True

    except Exception as error:

        print("Database connection failed.")
        print("Error type:", type(error).__name__)
        print("Check your database configuration.")

        return False

    finally:
        engine.dispose()


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":
    test_connection()
