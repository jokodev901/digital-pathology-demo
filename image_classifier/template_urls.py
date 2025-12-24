from django.urls import path
from .views import PLIPView


urlpatterns = [
    path('plip/', PLIPView.as_view(), name='plip'),
]
