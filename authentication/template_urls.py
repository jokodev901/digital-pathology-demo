from django.urls import path
from django.conf.urls import include
from django.views.generic.base import TemplateView
from .views import RegisterUser, HomeView


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register', RegisterUser.as_view(), name='signup'),
    path('home', HomeView.as_view(), name='home'),
]
