from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_FILE

engine = create_engine(
    f"sqlite:///{DATABASE_FILE}",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)