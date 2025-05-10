from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campus = Column(Enum("sangmyung", "seoul", name="campus_enum"), nullable=False)
    site = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
