from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class StatusEnum(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class MaterialTypeEnum(str, enum.Enum):
    note = "note"
    code = "code"
    image = "image"
    html = "html"
    file = "file"

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50), default="ti-book-2")
    color = Column(String(20), default="purple")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    topics = relationship("Topic", back_populates="course", cascade="all, delete-orphan")

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String(100), nullable=False)
    order = Column(Integer, default=0)
    status = Column(Enum(StatusEnum), default=StatusEnum.todo)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    course = relationship("Course", back_populates="topics")
    materials = relationship("Material", back_populates="topic", cascade="all, delete-orphan")

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String(200), nullable=False)
    type = Column(Enum(MaterialTypeEnum), nullable=False)
    content = Column(Text)
    file_path = Column(String(500))
    file_name = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    topic = relationship("Topic", back_populates="materials")
