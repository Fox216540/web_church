from pydantic import BaseModel
from datetime import date
from typing import Optional
class SermonSchema(BaseModel):
    title: str
    description: str
    autor: str
    video_url: str
    date: date

    class Config:
        orm_mode = True
        from_attributes = True
        json_encoders = {
            date: lambda v: v.strftime('%d.%m.%Y')  # Форматируем дату как дд.мм.гггг
        }


class EventSchema(BaseModel):
    name: str
    description: str
    date_start: date
    date_finish: Optional[date] = None  # Поле может быть None

    class Config:
        orm_mode = True
        from_attributes = True