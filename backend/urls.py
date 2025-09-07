"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# backend/urls.py
# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from downloader import views # Make sure this import is here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    
    # --- ADD URLS FOR THE NEW PAGES ---
    path('tutorial/', views.tutorial_view, name='tutorial'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    path('api/', include('downloader.urls')), # This handles our API calls
]
