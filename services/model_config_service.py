from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.model_config import ModelConfig
from app.schemas.model_config import ModelConfigCreateRequest, ModelConfigUpdateRequest


def mask_api_key(api_key: Optional[str]) -> Optional[str]:
    if not api_key:
        return None

    if len(api_key) <= 8:
        return "******"

    return api_key[:4] + "******" + api_key[-4:]


def to_model_config_response_data(config: ModelConfig) -> dict:
    return {
        "id": config.id,
        "name": config.name,
        "provider": config.provider,
        "model_name": config.model_name,
        "api_base_url": config.api_base_url,
        "api_key_masked": mask_api_key(config.api_key),
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "is_active": config.is_active,
        "remark": config.remark,
        "created_by": config.created_by,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
    }


def list_model_configs(db: Session) -> List[ModelConfig]:
    return db.query(ModelConfig).order_by(ModelConfig.id.desc()).all()


def get_model_config_by_id(db: Session, config_id: int) -> Optional[ModelConfig]:
    return db.query(ModelConfig).filter(ModelConfig.id == config_id).first()


def get_active_model_config(db: Session) -> Optional[ModelConfig]:
    return db.query(ModelConfig).filter(ModelConfig.is_active == True).first()


def create_model_config(
    db: Session,
    request: ModelConfigCreateRequest,
    user_id: int,
) -> ModelConfig:
    if request.is_active:
        db.query(ModelConfig).update({"is_active": False})

    config = ModelConfig(
        name=request.name,
        provider=request.provider,
        model_name=request.model_name,
        api_base_url=request.api_base_url,
        api_key=request.api_key,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        is_active=request.is_active,
        remark=request.remark,
        created_by=user_id,
    )

    db.add(config)
    db.commit()
    db.refresh(config)

    return config


def update_model_config(
    db: Session,
    config: ModelConfig,
    request: ModelConfigUpdateRequest,
) -> ModelConfig:
    update_data = request.model_dump(exclude_unset=True)

    if update_data.get("is_active") is True:
        db.query(ModelConfig).filter(ModelConfig.id != config.id).update(
            {"is_active": False}
        )

    for key, value in update_data.items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)

    return config


def delete_model_config(db: Session, config: ModelConfig) -> None:
    db.delete(config)
    db.commit()


def activate_model_config(db: Session, config: ModelConfig) -> ModelConfig:
    db.query(ModelConfig).update({"is_active": False})
    config.is_active = True
    db.commit()
    db.refresh(config)

    return config