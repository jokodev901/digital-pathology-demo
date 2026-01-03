from django.urls import path
from .template_views import PLIPView, PLIPImageView, AddFilterRowView, UpdateFilterStateView


urlpatterns = [
    path('plip/', PLIPView.as_view(), name='plip'),
    path('plip_data/', PLIPImageView.as_view(), name='plip_data'),
    path('add-filter-row/', AddFilterRowView.as_view(), name='add-filter-row'),
    path('update-filter-state/', UpdateFilterStateView.as_view(), name='update-filter-state'),
]
