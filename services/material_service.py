import os
import uuid
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.material import Material
from app.utils.file_parser import parse_file


BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_DIR / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx"}


def get_file_extension(filename: str) -> str:
    """
    获取文件后缀
    """
    if "." not in filename:
        return ""

    return filename.rsplit(".", 1)[-1].lower()


def generate_stored_name(filename: str) -> str:
    """
    生成服务器保存文件名

    目的：
    1. 避免中文路径问题
    2. 避免空格路径问题
    3. 避免重复文件名覆盖
    """
    ext = get_file_extension(filename)

    if not ext:
        return uuid.uuid4().hex

    return f"{uuid.uuid4().hex}.{ext}"


def save_file(file_bytes: bytes, stored_name: str) -> str:
    """
    保存文件到 uploads 目录
    """
    file_path = UPLOAD_DIR / stored_name

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return str(file_path)


def list_materials(db: Session) -> List[Material]:
    """
    查询课程资料列表
    """
    return db.query(Material).order_by(Material.id.desc()).all()


def get_material_by_id(db: Session, material_id: int) -> Optional[Material]:
    """
    根据ID查询课程资料
    """
    return db.query(Material).filter(Material.id == material_id).first()


def create_material(
    db: Session,
    file_bytes: bytes,
    filename: str,
    user_id: int,
) -> Material:
    """
    上传并解析课程资料
    """
    ext = get_file_extension(filename)

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("只支持 PDF、DOCX、PPTX 文件")

    stored_name = generate_stored_name(filename)
    file_path = save_file(file_bytes, stored_name)

    parse_status = "success"
    parse_error = None
    content = ""

    try:
        content = parse_file(file_path, ext)

        if not content:
            parse_status = "skipped"
            parse_error = "文件未解析出文本内容，可能是扫描版PDF或文件内容为空"
            content = ""

    except Exception as e:
        parse_status = "fail"
        parse_error = str(e)
        content = ""

    material = Material(
        name=filename,
        stored_name=stored_name,
        file_path=file_path,
        file_type=ext,
        file_size=os.path.getsize(file_path),
        content=content,
        parse_status=parse_status,
        parse_error=parse_error,
        created_by=user_id,
    )

    db.add(material)
    db.commit()
    db.refresh(material)

    return material


def delete_material(db: Session, material: Material) -> None:
    """
    删除课程资料

    删除逻辑：
    1. 删除本地文件
    2. 删除数据库记录
    """
    if material.file_path and os.path.exists(material.file_path):
        os.remove(material.file_path)

    db.delete(material)
    db.commit()