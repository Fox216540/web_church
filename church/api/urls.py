# api/urls.py
from django.urls import path
from .views import api
from ninja import NinjaAPI

import os

debug_value = os.getenv("DEBUG", "False")

# Если DEBUG явно не равно 'True', то устанавливаем docs_url=None
if debug_value != "True":
    api_docs = NinjaAPI(docs_url=None)
else:
    api_docs = NinjaAPI()

urlpatterns = [
    path("", api.urls),
]
