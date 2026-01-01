from django.urls import path, include
from .api_views import APIRootView, PLIPAPIListView, PLIPAPICreateView


urlpatterns = [
    path('', APIRootView.as_view(), name='api-v1-root'),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path('pliplist/', PLIPAPIListView.as_view(), name='plip-list'),
    path('plipinput/', PLIPAPICreateView.as_view(), name='plip-input'),
]
