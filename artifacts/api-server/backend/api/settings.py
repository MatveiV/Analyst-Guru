import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db
from backend.models import AiSetting

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/settings", tags=["settings"])


class AiSettingResponse(BaseModel):
    id: str
    provider: str
    has_api_key: bool


class AiSettingUpdate(BaseModel):
    provider: str
    api_key: str | None = None


@router.get("/ai", response_model=AiSettingResponse)
def get_ai_setting(db: Session = Depends(get_db)):
    setting = db.query(AiSetting).first()
    if not setting:
        return AiSettingResponse(id="", provider="anthropic", has_api_key=False)
    return AiSettingResponse(
        id=setting.id,
        provider=setting.provider,
        has_api_key=bool(setting.api_key),
    )


@router.put("/ai", response_model=AiSettingResponse)
def update_ai_setting(body: AiSettingUpdate, db: Session = Depends(get_db)):
    valid_providers = ["anthropic", "openai", "proxyapi"]
    if body.provider not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}")

    setting = db.query(AiSetting).first()
    if setting:
        setting.provider = body.provider
        if body.api_key is not None:
            setting.api_key = body.api_key
    else:
        setting = AiSetting(provider=body.provider, api_key=body.api_key)
        db.add(setting)

    db.commit()
    db.refresh(setting)
    return AiSettingResponse(
        id=setting.id,
        provider=setting.provider,
        has_api_key=bool(setting.api_key),
    )
