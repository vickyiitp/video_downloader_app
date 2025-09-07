# downloader/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Add the new path for getting video info
    path('info/', views.get_video_info, name='get_video_info'),
    path('download/', views.download_video, name='download_video'),
]