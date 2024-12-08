from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.engine import create_engine

from pydantic import BaseModel

from typing import List

engine = create_engine("sqlite:///database.db")

Base = declarative_base()


def get_db():
    with Session(engine) as session:
        yield session


class TextBase(Base):
    __tablename__ = "text"
    id = Column(Integer, primary_key=True)
    text = Column(String, unique=True)


class ProcessedTextModel(BaseModel):
    processed_text: List[str]


class SearchResultModel(BaseModel):
    query: str
    results: List[str]


class AddTextModel(BaseModel):
    id: int
    text: str

    class Config:
        from_attributes = True


Base.metadata.create_all(engine)
