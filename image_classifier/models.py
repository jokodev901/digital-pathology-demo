import base64
from django.db import models
from authentication.models import User


class PLIPImage(models.Model):
    blob_image = models.BinaryField()
    md5 = models.CharField(max_length=32, db_index=True)

    @property
    def image_base64(self):
        if not self.blob_image:
            return ""
        encoded = base64.b64encode(self.blob_image).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"

    def __str__(self):
        return self.md5


class PLIPLabel(models.Model):
    label = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.label


class PLIPSubmission(models.Model):
    image = models.ForeignKey(PLIPImage, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=100)


class PLIPScore(models.Model):
    label = models.ForeignKey(PLIPLabel, on_delete=models.CASCADE)
    score = models.FloatField()
    submission = models.ForeignKey(PLIPSubmission, on_delete=models.CASCADE, related_name='submission_scores')

    @property
    def rounded_score(self):
        return round(self.score, 2)

    def __str__(self):
        return self.score
