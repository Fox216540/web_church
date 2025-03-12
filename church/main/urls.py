from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='home'),
    path('sermons/', views.sermons, name='sermons'),
    path('confession_of_faith/', views.confession_of_faith, name='confession'),
]
