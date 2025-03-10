# api/urls.py
from django.urls import path
from .views import api
from ninja import NinjaAPI

import os

debug_value = os.getenv("DEBUG", "False")

# Если DEBUG явно не равно 'True', то устанавливаем docs_url=None
if debug_value != "True":
    api = NinjaAPI(docs_url=None)
else:
    api = NinjaAPI()

urlpatterns = [
    path("", api.urls),
]
