from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import config


def _ensure_database():
    """如果数据库不存在则创建"""
    engine = create_engine(
        f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}",
    )
    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS `{}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(
            config.MYSQL_DATABASE)))
        conn.commit()
    engine.dispose()


_ensure_database()

_engine = create_engine(
    f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DATABASE}",
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
