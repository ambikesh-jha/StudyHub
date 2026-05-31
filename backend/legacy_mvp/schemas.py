from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models import StatusEnum, MaterialTypeEnum

# --- Course Schemas ---
class CourseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = "ti-book-2"
    color: Optional[str] = "purple"

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class CourseOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon: str
    color: str
    created_at: datetime
    topic_count: Optional[int] = 0
    material_count: Optional[int] = 0
    class Config:
        from_attributes = True

# --- Topic Schemas ---
class TopicCreate(BaseModel):
    name: str
    order: Optional[int] = 0
    status: Optional[StatusEnum] = StatusEnum.todo

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    order: Optional[int] = None
    status: Optional[StatusEnum] = None

class TopicOut(BaseModel):
    id: int
    course_id: int
    name: str
    order: int
    status: StatusEnum
    created_at: datetime
    material_count: Optional[int] = 0
    class Config:
        from_attributes = True

# --- Material Schemas ---
class MaterialCreate(BaseModel):
    title: str
    type: MaterialTypeEnum
    content: Optional[str] = None

class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class MaterialOut(BaseModel):
    id: int
    topic_id: int
    title: str
    type: MaterialTypeEnum
    content: Optional[str]
    file_path: Optional[str]
    file_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
