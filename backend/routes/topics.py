from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Topic, Course, Material
from schemas import TopicCreate, TopicUpdate, TopicOut
from typing import List

router = APIRouter(prefix="/courses/{course_id}/topics", tags=["topics"])

@router.get("/", response_model=List[TopicOut])
def get_topics(course_id: int, db: Session = Depends(get_db)):
    topics = db.query(Topic).filter(Topic.course_id == course_id).order_by(Topic.order).all()
    result = []
    for t in topics:
        out = TopicOut.model_validate(t)
        out.material_count = len(t.materials)
        result.append(out)
    return result

@router.post("/", response_model=TopicOut, status_code=201)
def create_topic(course_id: int, data: TopicCreate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    topic = Topic(course_id=course_id, **data.model_dump())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    out = TopicOut.model_validate(topic)
    out.material_count = 0
    return out

@router.put("/{topic_id}", response_model=TopicOut)
def update_topic(course_id: int, topic_id: int, data: TopicUpdate, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id, Topic.course_id == course_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(topic, k, v)
    db.commit()
    db.refresh(topic)
    out = TopicOut.model_validate(topic)
    out.material_count = len(topic.materials)
    return out

@router.delete("/{topic_id}", status_code=204)
def delete_topic(course_id: int, topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id, Topic.course_id == course_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    db.delete(topic)
    db.commit()
