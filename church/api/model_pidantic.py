from pydantic import BaseModel, ConfigDict, field_validator, field_serializer
from datetime import date, datetime, time

class SermonSchema(BaseModel):
	title: str
	description: str | None
	author: str
	scripture: str | None   # <-- новое поле
	video_url: str
	date: date
	thumbnail: str  # вычисляется из video_url

	class Config:
		from_attributes = True
		json_encoders = {
			date: lambda v: v.strftime("%d.%m.%Y")
		}
		
class EventSchema(BaseModel):
	name: str
	description: str | None = None

	date_start: date
	time_start: time | None = None

	date_finish: date | None = None
	time_finish: time | None = None

	banner: str | None = None
	is_published: bool

	@field_validator("banner", mode="before")
	def convert_banner(cls, value):
		return value.url if value else None

	@field_serializer("date_start")
	def serialize_date_start(self, value: date):
		time_value = self.time_start
		if time_value:
			return f"{value.strftime('%d.%m.%Y')} {time_value.strftime('%H:%M')}"
		return value.strftime("%d.%m.%Y")

	@field_serializer("date_finish")
	def serialize_date_finish(self, value: date | None):
		if not value:
			return None

		time_value = self.time_finish
		if time_value:
			return f"{value.strftime('%d.%m.%Y')} {time_value.strftime('%H:%M')}"
		return value.strftime("%d.%m.%Y")

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
	leader: str
	photo_of_leader: str | None = None
	location: str
	meeting_time: str

	@field_validator("photo_of_leader", mode="before")
	def convert_photo(cls, value):
		return value.url if value else None

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