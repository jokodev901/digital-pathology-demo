from rest_framework import serializers
from rest_framework.fields import ReadOnlyField

from ..models import PLIPImage, PLIPSubmission, PLIPScore, PLIPLabel


class PLIPImageSerializer(serializers.ModelSerializer):
    image_base64 = ReadOnlyField()

    class Meta:
        model = PLIPImage
        exclude = ('blob_image',)


class PLIPLabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = PLIPLabel
        fields = '__all__'


class PLIPScoreSerializer(serializers.ModelSerializer):
    label = PLIPLabelSerializer(read_only=True)
    rounded_score = ReadOnlyField()

    class Meta:
        model = PLIPScore
        fields = '__all__'


class PLIPSubmissionSerializer(serializers.ModelSerializer):
    image = PLIPImageSerializer(read_only=True)
    submission_scores = PLIPScoreSerializer(many=True, read_only=True)

    class Meta:
        model = PLIPSubmission
        fields = '__all__'
