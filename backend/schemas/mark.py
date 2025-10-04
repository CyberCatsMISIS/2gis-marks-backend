from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime




class MarkBase(BaseModel):
    text: str = "Уютное кафе с розетками и Wi-Fi"
    tags: list[str] = ["кафе", "wi-fi", "розетки"]
    latitude: float = 59.9386
    longitude: float = 30.3141


class SMarkCreate(MarkBase):
    pass


class SMarkUpdate(MarkBase):
    pass


class SMark(MarkBase):
    id: int
    created_at: datetime
    updated_at: datetime