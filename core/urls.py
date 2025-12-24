from django.urls import path
from django.conf.urls import include
from django.views.generic.base import TemplateView
from .views import set_theme, HomeView


urlpatterns = [
    path('set-theme/', set_theme, name='set_theme'),
    path('', HomeView.as_view(), name='home'),
]