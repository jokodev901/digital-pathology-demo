from django.urls import path, include
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView, SpectacularRedocView
from .api_views import PLIPAPIListView, PLIPAPICreateView


urlpatterns = [
    path('pliplist/', PLIPAPIListView.as_view(), name='plip-list'),
    path('plipinput/', PLIPAPICreateView.as_view(), name='plip-input'),
    path('schema/', SpectacularAPIView.as_view(permission_classes=(IsAuthenticated, )), name='schema'),
    path('schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema', permission_classes=(IsAuthenticated, )), name='swagger-ui'),
    path('schema/redoc/',
         SpectacularRedocView.as_view(url_name='schema', permission_classes=(IsAuthenticated, )), name='redoc'),
]