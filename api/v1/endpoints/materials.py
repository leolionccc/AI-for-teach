from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.users import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.material import MaterialDetailResponse, MaterialListResponse
from app.schemas.response import ApiResponse
from app.services.material_service import (
    create_material,
    delete_material,
    get_material_by_id,
    list_materials,
)


router = APIRouter()


@router.get("", response_model=ApiResponse)
def list_all_materials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查询课程资料列表

    注意：
    列表接口不返回 content，避免响应体过大导致前端代理断开。
    """
    materials = list_materials(db)

    return ApiResponse(
        code=200,
        message="success",
        data=[MaterialListResponse.model_validate(item) for item in materials],
    )


@router.get("/{material_id}", response_model=ApiResponse)
def get_material_detail(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查询课程资料详情

    查看解析内容时调用这个接口。
    """
    material = get_material_by_id(db, material_id)

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资料不存在",
        )

    return ApiResponse(
        code=200,
        message="success",
        data=MaterialDetailResponse.model_validate(material),
    )


@router.post("", response_model=ApiResponse)
async def upload_material(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    上传课程资料
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空",
        )

    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="上传文件不能为空",
            )

        material = create_material(
            db=db,
            file_bytes=file_bytes,
            filename=file.filename,
            user_id=current_user.id,
        )

        return ApiResponse(
            code=200,
            message="上传成功",
            data=MaterialListResponse.model_validate(material),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败：{str(e)}",
        )


@router.delete("/{material_id}", response_model=ApiResponse)
def remove_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除课程资料
    """
    material = get_material_by_id(db, material_id)

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资料不存在",
        )

    delete_material(db, material)

    return ApiResponse(
        code=200,
        message="删除成功",
        data=None,
    )