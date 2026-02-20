from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = "postgresql://postgres:postgres@localhost:5433/postgres"
engine = create_engine(DB_URL)
SessionFactory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()
