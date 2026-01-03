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