from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date, datetime

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
	url: str
	drive_date: datetime
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
		
class BaseDocumentSchema(BaseModel):
	doc_type: str

	model_config = ConfigDict(from_attributes=True)

	@field_validator("doc_type", mode="before")
	def convert_doc_type(cls, value):
		return value.code


class ChurchDocumentListSchema(BaseDocumentSchema):
	slug: str
	title: str


class ChurchDocumentDetailSchema(BaseDocumentSchema):
	title: str
	content: str
	updated_at: datetime
	
class ChurchDocumentTypeSchema(BaseModel):
	code: str
	name: str

	model_config = ConfigDict(from_attributes=True)

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
		
class ContactItemSchema(BaseModel):
	id: int
	title: str
	value: str
	link: str | None = None
	icon: str
	order: int

	class Config:
		from_attributes = True


class ContactsResponseSchema(BaseModel):
	contacts: list[ContactItemSchema]
	map_embed: str | None = None
		
class SeoPageSchema(BaseModel):
	slug: str
	title: str
	description: str

	class Config:
		from_attributes = True