from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Material, Topic, MaterialTypeEnum
from schemas import MaterialCreate, MaterialUpdate, MaterialOut
from typing import List, Optional
import os, shutil, uuid
from dotenv import load_dotenv

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/topics/{topic_id}/materials", tags=["materials"])

@router.get("/", response_model=List[MaterialOut])
def get_materials(topic_id: int, db: Session = Depends(get_db)):
    return db.query(Material).filter(Material.topic_id == topic_id).order_by(Material.created_at).all()

@router.post("/", response_model=MaterialOut, status_code=201)
def create_material(topic_id: int, data: MaterialCreate, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    material = Material(topic_id=topic_id, **data.model_dump())
    db.add(material)
    db.commit()
    db.refresh(material)
    return material

@router.post("/upload", response_model=MaterialOut, status_code=201)
async def upload_file(
    topic_id: int,
    title: str = Form(...),
    type: MaterialTypeEnum = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    material = Material(
        topic_id=topic_id,
        title=title,
        type=type,
        file_path=file_path,
        file_name=file.filename
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material

@router.get("/file/{material_id}")
def serve_file(topic_id: int, material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id, Material.topic_id == topic_id).first()
    if not material or not material.file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(material.file_path, filename=material.file_name)

@router.put("/{material_id}", response_model=MaterialOut)
def update_material(topic_id: int, material_id: int, data: MaterialUpdate, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id, Material.topic_id == topic_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(material, k, v)
    db.commit()
    db.refresh(material)
    return material

@router.delete("/{material_id}", status_code=204)
def delete_material(topic_id: int, material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id, Material.topic_id == topic_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if material.file_path and os.path.exists(material.file_path):
        os.remove(material.file_path)
    db.delete(material)
    db.commit()
