# api/urls.py
from django.urls import path
from ninja import NinjaAPI

import os

debug = os.getenv("DEBUG", "False").lower() == "true"
api = NinjaAPI(docs_url="/docs" if debug else None)

# Если DEBUG явно не равно 'True', то устанавливаем docs_url=None
from . import views  # Эндпоинты регистрируются на этом экземпляре

urlpatterns = [
    path("", api.urls),
]
