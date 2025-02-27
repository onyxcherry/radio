from config import Settings
from kink import di
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import lru_cache


def setup_engine():
    settings = di[Settings]
    engine = create_engine(
        settings.sqlalchemy_database_url, connect_args={"check_same_thread": False}
    )
    return engine


@lru_cache
def sessionLocal():
    engine = setup_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal
