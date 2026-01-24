from sqlalchemy import Column, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Auth(Base):
    __tablename__ = "auth"

    username = Column(String(100), primary_key=True, nullable=False, index=True)
    hashed_pswd = Column(LargeBinary, nullable=False)