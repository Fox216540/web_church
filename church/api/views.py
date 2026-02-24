from ninja.pagination import paginate, PageNumberPagination
from typing import List
from django.shortcuts import get_object_or_404
from .models import (
	Sermon,
	Event,
	Content,
	CategoryOfContent,
	HomeGroup,
	ChurchDocumentType,
	ChurchDocument,
	Ministry,
	ContactItem,
	ContactSettings,
	ChurchBoard,
	SeoPage)
from .model_pidantic import (
	SermonSchema,
	EventSchema,
	ContentSchema,
	CategorySchema,
	HomeGroupSchema,
	ChurchDocumentTypeSchema,
	ChurchDocumentListSchema,
	ChurchDocumentDetailSchema,
	MinistrySchema,
	ContactsResponseSchema,
	ChurchBoardSchema,
	SeoPageSchema
)
from .urls import api
@api.get("/sermons/", response=List[SermonSchema])
@paginate(PageNumberPagination, page_size=6)
def get_sermons(request):
	return Sermon.objects.order_by("-date")

@api.get("/latest_3_sermons/", response=List[SermonSchema])
def get_latest_sermons(request):
	return Sermon.objects.order_by("-date")[:3]

@api.get("/events/", response=List[EventSchema])
def get_events(request):
	return Event.objects.filter(is_published=True)

@api.get("/categories/", response=List[CategorySchema])
def get_categories(request):
	return CategoryOfContent.objects.all()

@api.get("/content/", response=List[ContentSchema])
@paginate(PageNumberPagination, page_size=20)
def get_contents(request, category: str | None = None):
	qs = Content.objects.select_related("category")

	if category:
		qs = qs.filter(category__slug=category)

	return qs
@api.get("/home-groups/", response=list[HomeGroupSchema])
def get_home_groups(request):
	return HomeGroup.objects.all()

@api.get("/document-types/", response=list[ChurchDocumentTypeSchema])
def get_document_types(request):
	return ChurchDocumentType.objects.all()

@api.get("/documents/", response=list[ChurchDocumentListSchema])
def get_documents(request):
	return ChurchDocument.objects.select_related("doc_type").all()

@api.get("/documents/{doc_type_code}/", response=ChurchDocumentDetailSchema)
def get_document(request, doc_type_code: str):
	return get_object_or_404(
		ChurchDocument,
		doc_type__code=doc_type_code
	)

@api.get("/ministries/", response=list[MinistrySchema])
def get_ministries(request):
	return [
		{
			"name": m.name,
			"description": m.description,
			"leader": m.leader,
			"phone": m.phone,
			"email": m.email,
			"telegram": m.telegram,
			"whatsapp": m.whatsapp,
			"instagram": m.instagram,
			"photo": m.photo.url if m.photo else None,
		}
		for m in Ministry.objects.all()
	]

@api.get("/church-board/", response=list[ChurchBoardSchema])
def get_church_board(request):
	objects = ChurchBoard.objects.all()

	result = []
	for obj in objects:
		photo_url = None
		if obj.photo:
			photo_url = request.build_absolute_uri(obj.photo.url)

		result.append({
			"name": obj.name,
			"role": obj.role,
			"photo": photo_url,
			"short_bio": obj.short_bio,
			"phone": obj.phone,
			"email": obj.email,
			"telegram": obj.telegram,
		})

	return result

@api.get("/contacts/", response=ContactsResponseSchema)
def get_contacts(request):
	contacts = ContactItem.objects.filter(is_active=True).order_by("order")
	settings = ContactSettings.objects.first()
	return {
		"contacts": contacts,
		"map_embed": settings.map_embed if settings else None
	}

@api.get("/seo/{slug}/", response=SeoPageSchema)
def get_seo(request, slug: str):
	return SeoPage.objects.get(slug=slug)