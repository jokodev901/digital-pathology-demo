from django.urls import path
from .views import HomeView, UserProfileView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]