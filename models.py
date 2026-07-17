from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from datetime import datetime

Base = declarative_base()


class Job(Base):

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)

    uuid = Column(String, unique=True)

    status = Column(String)

    progress = Column(Integer)

    total = Column(Integer)

    created = Column(DateTime, default=datetime.utcnow)