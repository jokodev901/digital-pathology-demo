from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import PLIPImage, PLIPSubmission, PLIPScore, PLIPLabel


@admin.register(PLIPImage)
class PLIPImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_preview', 'md5')
    readonly_fields = ('image_preview', 'md5')
    search_fields = ('id', 'md5')

    def image_preview(self, obj):
        """
        Converts the binary blob into base64 encoded thumbnail.
        """
        if obj.blob_image:
            base64_data = obj.image_base64

            # Return HTML img tag for rendering in admin screen
            return mark_safe(
                f'<img src="{base64_data}" '
                f'style="width: 100px; height: auto; border-radius: 4px;" />'
            )
        return "No Image"

    image_preview.short_description = 'Thumbnail'


@admin.register(PLIPSubmission)
class PLIPSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'filename', 'user', 'created_at')
    search_fields = ('id', 'filename')


@admin.register(PLIPScore)
class PLIPScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'score', 'rounded_score', 'submission__id')
    search_fields = ('id', 'submission__id')
    readonly_fields = ('rounded_score', )


@admin.register(PLIPLabel)
class PLIPLabelAdmin(admin.ModelAdmin):
    pass