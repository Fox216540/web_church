
from ninja.pagination import paginate, PageNumberPagination
from ninja import NinjaAPI
from typing import List
from .models import Sermon, Event
from .model_pidantic import SermonSchema,EventSchema

api = NinjaAPI()

@api.get("/sermons/", response=List[SermonSchema])
@paginate(PageNumberPagination, page_size=6)
def get_sermons_10(request):
    sermons = Sermon.objects.order_by('-date')  # Получаем все проповеди
    return [SermonSchema.from_orm(sermon) for sermon in sermons]

@api.get("/lates_3_sermons/", response=List[SermonSchema])
def get_sermons_3(request):
    # Фильтруем записи по полю publish_date, выбираем только те, что опубликованы за последние 7 дней
    sermons = Sermon.objects.filter().order_by('-date')[:3]
    return [SermonSchema.from_orm(sermon) for sermon in sermons]

@api.get("/events/", response=List[EventSchema])
def get_events(request):
    events = Event.objects.all()
    return events
