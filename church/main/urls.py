from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='home'),
    path('sermons/', views.sermons, name='sermons'),
    path('docs/', views.docs, name='docs'),
	path('doc/', views.doc, name='doc'),
	path('home-group/', views.home_groups, name='home-group'),
	path('board/', views.board, name='board'),
	path('content/', views.content, name='content'),
]
