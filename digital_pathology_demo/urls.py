"""
URL configuration for digital_pathology_demo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from core import urls as core_urls
from authentication import template_urls as auth_temp_urls
from image_classifier import template_urls as image_temp_urls
from image_classifier import api_urls as image_api_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include(auth_temp_urls)),
    path('imageclassifier/', include(image_temp_urls)),
    path('api/v1/', include(image_api_urls)),
    path('', include(core_urls)),
]