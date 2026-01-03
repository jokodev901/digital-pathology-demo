from django.urls import path
from .template_views import PLIPView, PLIPImageView, add_filter_row


urlpatterns = [
    path('plip/', PLIPView.as_view(), name='plip'),
    path('plip_data/', PLIPImageView.as_view(), name='plip_data'),
    path('add-filter-row/', add_filter_row, name='add-filter-row')
]
