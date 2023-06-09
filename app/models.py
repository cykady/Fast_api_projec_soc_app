# This file contains the models for the database in SQLAlchemy

from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer,nullable=False,primary_key=True,index=True)
    title = Column(String,nullable=False)
    content = Column(String,nullable=False)
    published = Column(Boolean,server_default="True",nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(),nullable=False)
    owner_id = Column(Integer,ForeignKey("users.id",ondelete='CASCADE'),nullable=False)
    owner = relationship("User")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer,nullable=False ,primary_key=True, index=True)
    email = Column(String,nullable=False, unique=True)
    password = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),server_default=func.now(),nullable=False)

class Votes(Base):
    __tablename__ = 'votes'
    user_id = Column(Integer,ForeignKey("users.id",ondelete='CASCADE'),nullable=False,primary_key=True)
    post_id = Column(Integer,ForeignKey("posts.id",ondelete='CASCADE'),nullable=False,primary_key=True)