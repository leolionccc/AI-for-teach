from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SystemLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    module: str
    action: str
    method: Optional[str] = None
    path: Optional[str] = None
    status: str
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }