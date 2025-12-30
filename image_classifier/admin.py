from django.contrib import admin
from .models import PLIPImage, PLIPSubmission, PLIPScore, PLIPLabel

admin.site.register(PLIPImage)
admin.site.register(PLIPSubmission)
admin.site.register(PLIPScore)
admin.site.register(PLIPLabel)