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
    label = serializers.SlugRelatedField(many=False, read_only=True, slug_field='label')
    rounded_score = ReadOnlyField()

    class Meta:
        model = PLIPScore
        exclude = ('submission',)


class PLIPSubmissionSerializer(serializers.ModelSerializer):
    image = PLIPImageSerializer(read_only=True)
    expected_label = serializers.SlugRelatedField(many=False, read_only=True, slug_field='label')
    submission_scores = PLIPScoreSerializer(many=True, read_only=True)

    class Meta:
        model = PLIPSubmission
        fields = '__all__'


class PLIPAPIInputSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    expected_label = serializers.CharField(required=True, allow_blank=False, allow_null=True, max_length=255)
    labels = serializers.CharField(required=True, allow_blank=True, allow_null=False, max_length=255)


class PLIPAPIOutputSerializer(serializers.ModelSerializer):
    submission_scores = PLIPScoreSerializer(many=True, read_only=True)
    expected_label = serializers.SlugRelatedField(many=False, read_only=True, slug_field='label')

    class Meta:
        model = PLIPSubmission
        exclude = ('image',)


class PLIPAPILabelFilterSerializer(serializers.Serializer):
    label = serializers.CharField(required=False, allow_blank=False, allow_null=False, max_length=255)
    min = serializers.FloatField(required=False, allow_null=False)
    max = serializers.FloatField(required=False, allow_null=False)


class PLIPAPIListSerializer(serializers.Serializer):
    labels = PLIPLabelSerializer(many=True, read_only=True, required=False)
    min_date = serializers.DateField(required=False, allow_null=False,
                                     format='%Y-%m-%d %H:%M:%S', input_formats=['%Y-%m-%d'])
    max_date = serializers.DateField(required=False, allow_null=False,
                                     format='%Y-%m-%d %H:%M:%S', input_formats=['%Y-%m-%d'])