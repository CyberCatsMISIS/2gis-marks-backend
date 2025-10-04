from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime




class MarkBase(BaseModel):
    text: str = "Уютное кафе с розетками и Wi-Fi"
    latitude: float = 59.9386
    longitude: float = 30.3141


class SMarkCreate(MarkBase):
    pass


class SMarkUpdate(MarkBase):
    pass


class SMark(MarkBase):
    id: int
    tags: list[str]
    created_at: datetime
    updated_at: datetime