from sqlalchemy import Column, Integer, String
from app.database.db import Base

class TestModel(Base):
    __tablename__ = "test_table"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    string = Column(String(255), nullable=False)

       # 테이블이 이미 존재하면 덮어쓰도록 설정
    __table_args__ = {'extend_existing': True}
