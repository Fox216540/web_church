import io
import requests
from logger import status_logger
from alarm import tg_alarm
from django.http import Http404, HttpResponse, StreamingHttpResponse
from ninja.pagination import paginate, PageNumberPagination
from django.shortcuts import get_object_or_404
from PIL import Image
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


def _is_heic_content_type(content_type: str) -> bool:
	content_type = (content_type or "").lower()
	return "image/heic" in content_type or "image/heif" in content_type


def _is_octet_stream_content_type(content_type: str) -> bool:
	return (content_type or "").lower().startswith("application/octet-stream")


def _is_heic_by_disposition(content_disposition: str) -> bool:
	value = (content_disposition or "").lower()
	return ".heic" in value or ".heif" in value


def _build_cache_headers(response):
	response["Cache-Control"] = "public, max-age=86400"
	return response


def _convert_heic_to_jpeg_response(raw_bytes: bytes):
	try:
		image = Image.open(io.BytesIO(raw_bytes))
		if image.mode not in ("RGB", "L"):
			image = image.convert("RGB")

		output = io.BytesIO()
		image.save(output, format="JPEG", quality=90, optimize=True)
		output.seek(0)
		return _build_cache_headers(HttpResponse(output.read(), content_type="image/jpeg"))
	except Exception:
		return None


def _fallback_drive_thumbnail(file_id: str):
	thumb_url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w2000"
	try:
		r = requests.get(thumb_url, stream=True, timeout=15, allow_redirects=True)
	except requests.RequestException:
		return None

	if r.status_code != 200:
		return None
	content_type = (r.headers.get("Content-Type") or "").lower()
	if not content_type.startswith("image/"):
		return None

	return _build_cache_headers(
		StreamingHttpResponse(
			r.iter_content(chunk_size=64 * 1024),
			content_type=content_type,
		)
	)

@api.get("/sermons/", response=list[SermonSchema])
@paginate(PageNumberPagination, page_size=6)
def get_sermons(request):
	return Sermon.objects.order_by("-date")

@api.get("/latest_3_sermons/", response=list[SermonSchema])
def get_latest_sermons(request):
	return Sermon.objects.order_by("-date")[:3]

@api.get("/events/", response=list[EventSchema])
def get_events(request):
	return Event.objects.filter(is_published=True)

@api.get("/categories/", response=list[CategorySchema])
def get_categories(request):
	return CategoryOfContent.objects.all()

@api.get("/content/", response=list[ContentSchema])
@paginate(PageNumberPagination, page_size=9)
def get_contents(request, category: str | None = None):
	status_logger.info("GET /content/ requested with category=%s", category)
	qs = Content.objects.select_related("category")

	if category:
		qs = qs.filter(category__slug=category)

	return [
		{
			"id": obj.id,
			"photo_url": request.build_absolute_uri(f"/api/drive-image/{obj.photo_id}"),
			"drive_date": obj.drive_date,
			"category_slug": obj.category.slug,
		}
		for obj in qs
	]
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
			"whatsapp": obj.whatsapp,
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

@api.get("/drive-image/{file_id}")
def drive_image(request, file_id: str):
	status_logger.info("GET /drive-image requested for file_id=%s", file_id)

	url = f"https://drive.google.com/uc?export=download&id={file_id}"

	try:
		r = requests.get(url, stream=True, timeout=15, allow_redirects=True)
	except requests.RequestException as e:
		tg_alarm.alarm(f"Drive request failed for file_id={file_id}:", e)
		raise Http404()

	if r.status_code != 200:
		tg_alarm.alarm(f"Drive returned status {r.status_code} for file_id={file_id}")
		raise Http404()

	content_type = (r.headers.get("Content-Type") or "").lower()
	content_disposition = r.headers.get("Content-Disposition") or ""
	is_heic_like = _is_heic_content_type(content_type) or _is_heic_by_disposition(content_disposition)
	is_unknown_binary = _is_octet_stream_content_type(content_type)
	is_regular_image = content_type.startswith("image/") and not is_heic_like

	if is_regular_image:
		response = _build_cache_headers(StreamingHttpResponse(
			r.iter_content(chunk_size=64 * 1024),
			content_type=content_type
		))
		return response

	if is_heic_like or is_unknown_binary or not content_type.startswith("image/"):
		converted = _convert_heic_to_jpeg_response(r.content)
		if converted is not None:
			return converted

		thumbnail = _fallback_drive_thumbnail(file_id)
		if thumbnail is not None:
			return thumbnail

		tg_alarm.alarm(
			f"Drive image resolve failed for file_id={file_id}, content_type='{content_type}', "
			f"content_disposition='{content_disposition}'"
		)
		raise Http404()

	tg_alarm.alarm(f"Unexpected Drive response for file_id={file_id}, content_type='{content_type}'")
	raise Http404()

@api.get("/seo/{slug}/", response=SeoPageSchema)
def get_seo(request, slug: str):
	return SeoPage.objects.get(slug=slug)
