# api/urls.py
from django.urls import path
from .views import api
from ninja import NinjaAPI

import os

if os.getenv('DEBUG') is False:
    api = NinjaAPI(docs_url=None)

urlpatterns = [
    path("", api.urls),
]
