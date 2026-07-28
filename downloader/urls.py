# downloader/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('download/', views.download_video, name='download_video'),
    path('info/', views.fetch_info, name='fetch_info'),
]