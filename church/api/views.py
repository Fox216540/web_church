from ninja.pagination import paginate, PageNumberPagination
from typing import List
from .models import (
	Sermon,
    Event,
	Content,
	CategoryOfContent,
	HomeGroup,
	ChurchDocument,
	Ministry,
	ChurchContact,
	ChurchBoard,
	SeoPage)
from .model_pidantic import (
    SermonSchema,
    EventSchema,
    ContentSchema,
    CategorySchema,
	HomeGroupSchema,
	ChurchDocumentSchema,
	MinistrySchema,
	ChurchContactSchema,
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

@api.get("/documents/", response=ChurchDocumentSchema)
def get_document(request, doc_type: str):
    return ChurchDocument.objects.get(doc_type=doc_type)

@api.get("/documents/{doc_type}/", response=ChurchDocumentSchema)
def get_document(request, doc_type: str):
    return ChurchDocument.objects.get(doc_type=doc_type)

@api.get("/ministries/", response=list[MinistrySchema])
def get_ministries(request):
    return Ministry.objects.all()

@api.get("/church-board/", response=list[ChurchBoardSchema])
def get_church_board(request):
    return ChurchBoard.objects.all()

@api.get("/contacts/", response=ChurchContactSchema)
def get_contacts(request):
    return ChurchContact.objects.first()

@api.get("/seo/{slug}/", response=SeoPageSchema)
def get_seo(request, slug: str):
    return SeoPage.objects.get(slug=slug)