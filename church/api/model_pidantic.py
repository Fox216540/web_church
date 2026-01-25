from pydantic import BaseModel
from datetime import date

class SermonSchema(BaseModel):
    title: str
    description: str | None
    author: str
    video_url: str
    date: date
    thumbnail: str   # вычисляется из video_url

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.strftime("%d.%m.%Y")
        }
	    
class EventSchema(BaseModel):
    name: str
    description: str | None
    date_start: str
    date_finish: str | None
    banner: str | None
    is_published: bool

    class Config:
        from_attributes = True
	    
class CategorySchema(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True
	    
class ContentSchema(BaseModel):
    id: int
    title: str
    url: str
    category: CategorySchema

    class Config:
        from_attributes = True
	    
class HomeGroupSchema(BaseModel):
    name: str
    leader: str
    photo_of_leader: str | None
    location: str
    meeting_time: str

    class Config:
        from_attributes = True
	    
class ChurchDocumentSchema(BaseModel):
    doc_type: str
    title: str
    content: str
    updated_at: str

    class Config:
        from_attributes = True
        
class MinistrySchema(BaseModel):
    name: str
    description: str
    leader: str
    photo: str | None

    phone: str | None
    email: str | None
    telegram: str | None
    whatsapp: str | None
    instagram: str | None

    class Config:
        from_attributes = True
        
class ChurchBoardSchema(BaseModel):
    name: str
    role: str
    photo: str | None
    short_bio: str | None

    phone: str | None
    email: str | None
    telegram: str | None

    class Config:
        from_attributes = True
        
class ChurchContactSchema(BaseModel):
    address: str
    phone: str
    email: str
    map_url: str

    class Config:
        from_attributes = True
        
class SeoPageSchema(BaseModel):
    slug: str
    title: str
    description: str

    class Config:
        from_attributes = True