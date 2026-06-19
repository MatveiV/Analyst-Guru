import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database import get_db
from backend.models import AiSetting

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/settings", tags=["settings"])

PROVIDER_DEFAULTS = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openrouter/free",
        "max_tokens": 4096,
        "temperature": 0.2,
    },
    "anthropic": {
        "base_url": None,
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4096,
        "temperature": 0.2,
    },
    "openai": {
        "base_url": None,
        "model": "gpt-4o",
        "max_tokens": 4096,
        "temperature": 0.2,
    },
    "proxyapi": {
        "base_url": "https://api.proxyapi.ru/openai/v1",
        "model": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0.2,
    },
}


class AiSettingResponse(BaseModel):
    id: str
    provider: str
    has_api_key: bool
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class AiSettingUpdate(BaseModel):
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


def _merge_defaults(setting: AiSetting | None) -> AiSettingResponse:
    if setting is None:
        defaults = PROVIDER_DEFAULTS.get("openrouter", {})
        return AiSettingResponse(
            id="", provider="openrouter", has_api_key=False,
            base_url=defaults.get("base_url"),
            model=defaults.get("model"),
            max_tokens=defaults.get("max_tokens"),
            temperature=defaults.get("temperature"),
        )
    defaults = PROVIDER_DEFAULTS.get(setting.provider, {})
    return AiSettingResponse(
        id=setting.id,
        provider=setting.provider,
        has_api_key=bool(setting.api_key),
        base_url=setting.base_url or defaults.get("base_url"),
        model=setting.model or defaults.get("model"),
        max_tokens=setting.max_tokens if setting.max_tokens is not None else defaults.get("max_tokens"),
        temperature=setting.temperature if setting.temperature is not None else defaults.get("temperature"),
    )


@router.get("/ai", response_model=AiSettingResponse)
def get_ai_setting(db: Session = Depends(get_db)):
    setting = db.query(AiSetting).first()
    return _merge_defaults(setting)


@router.put("/ai", response_model=AiSettingResponse)
def update_ai_setting(body: AiSettingUpdate, db: Session = Depends(get_db)):
    valid_providers = list(PROVIDER_DEFAULTS.keys())
    if body.provider not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}")

    setting = db.query(AiSetting).first()
    if setting:
        setting.provider = body.provider
        if body.api_key is not None:
            setting.api_key = body.api_key
        if body.base_url is not None:
            setting.base_url = body.base_url
        if body.model is not None:
            setting.model = body.model
        if body.max_tokens is not None:
            setting.max_tokens = body.max_tokens
        if body.temperature is not None:
            setting.temperature = body.temperature
    else:
        setting = AiSetting(
            provider=body.provider,
            api_key=body.api_key,
            base_url=body.base_url,
            model=body.model,
            max_tokens=body.max_tokens,
            temperature=body.temperature,
        )
        db.add(setting)

    db.commit()
    db.refresh(setting)
    return _merge_defaults(setting)
