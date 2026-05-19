import os
from sqlalchemy import create_engine, text

def _create_engine():
        db_host = os.getenv("DB_HOST", "postgres")
        db_name = os.getenv("DB_NAME", "my_db")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD")

        if db_password is None:
            raise RuntimeError("Database password is not set. Set DB_PASSWORD in the environment.")

        return create_engine(
            f'postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}'
        )