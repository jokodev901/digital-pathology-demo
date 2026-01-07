import base64
from django.db import models
from core.models import TimestampBaseModel
from authentication.models import User


class PLIPImage(TimestampBaseModel):
    blob_image = models.BinaryField()
    md5 = models.CharField(max_length=32, db_index=True)

    @property
    def image_base64(self):
        if not self.blob_image:
            return ""
        encoded = base64.b64encode(self.blob_image).decode('utf-8')
        return encoded

    def __str__(self):
        return self.md5


class PLIPLabel(models.Model):
    label = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.label


class PLIPSubmission(TimestampBaseModel):
    image = models.ForeignKey(PLIPImage, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expected_label = models.ForeignKey(PLIPLabel, on_delete=models.DO_NOTHING, blank=True, null=True)
    filename = models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)


class PLIPScore(models.Model):
    label = models.ForeignKey(PLIPLabel, on_delete=models.DO_NOTHING)
    score = models.FloatField(db_index=True)
    submission = models.ForeignKey(PLIPSubmission, on_delete=models.CASCADE, related_name='submission_scores')

    @property
    def rounded_score(self):
        return round(self.score, 2)

    def __str__(self):
        return str(self.score)
