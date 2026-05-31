from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Course, Topic, Material
from schemas import CourseCreate, CourseUpdate, CourseOut
from typing import List

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("/", response_model=List[CourseOut])
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    result = []
    for c in courses:
        topic_ids = [t.id for t in c.topics]
        material_count = db.query(Material).filter(Material.topic_id.in_(topic_ids)).count() if topic_ids else 0
        out = CourseOut.model_validate(c)
        out.topic_count = len(c.topics)
        out.material_count = material_count
        result.append(out)
    return result

@router.post("/", response_model=CourseOut, status_code=201)
def create_course(data: CourseCreate, db: Session = Depends(get_db)):
    course = Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    out = CourseOut.model_validate(course)
    out.topic_count = 0
    out.material_count = 0
    return out

@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    topic_ids = [t.id for t in course.topics]
    material_count = db.query(Material).filter(Material.topic_id.in_(topic_ids)).count() if topic_ids else 0
    out = CourseOut.model_validate(course)
    out.topic_count = len(course.topics)
    out.material_count = material_count
    return out

@router.put("/{course_id}", response_model=CourseOut)
def update_course(course_id: int, data: CourseUpdate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(course, k, v)
    db.commit()
    db.refresh(course)
    out = CourseOut.model_validate(course)
    out.topic_count = len(course.topics)
    return out

@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
