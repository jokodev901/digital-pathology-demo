from django.urls import path
from .template_views import PLIPView, PLIPImageView


urlpatterns = [
    path('plip/', PLIPView.as_view(), name='plip'),
    path('plip_data/', PLIPImageView.as_view(), name='plip_data'),
]
