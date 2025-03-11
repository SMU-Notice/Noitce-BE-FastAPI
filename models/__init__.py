from sqlalchemy import Column, Integer, String
from database.db import Base

class StringModel(Base):
    __tablename__ = "test_table"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    string = Column(String(255), nullable=False)
