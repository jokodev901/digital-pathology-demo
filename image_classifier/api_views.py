import hashlib
import io

from PIL import Image

from django.db import transaction
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import extend_schema

from authentication.permissions import IsContributor
from .models import PLIPSubmission, PLIPImage, PLIPLabel, PLIPScore
from .serializers.plip_serializers import PLIPAPIListInputSerializer, PLIPAPICreateSerializer, PLIPSubmissionSerializer
from .services.plip import PLIPClassifier


class PLIPAPIListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PLIPAPIListInputSerializer

    def get_queryset(self):
        queryset = PLIPSubmission.objects.all()
        serialized_input = self.serializer_class(data=self.request.data)
        serialized_input.is_valid(raise_exception=True)

        min_date = serialized_input.validated_data.get('min_date', None)
        max_date = serialized_input.validated_data.get('max_date', None)
        labels = serialized_input.validated_data.get('labels', None)

        q_and_objects = Q()
        q_or_objects = Q()
        has_label_filters = False

        if min_date:
            q_and_objects &= Q(created_at__gte=min_date)

        if max_date:
            q_and_objects &= Q(created_at__lte=max_date)

        if labels:
            for obj in labels:
                q_label_object = Q()

                if 'label' in obj:
                    has_label_filters = True
                    q_label_object &= Q(submission_scores__label__label__icontains=obj['label'])

                    if 'min' in obj:
                        q_label_object &= Q(submission_scores__score__gte=obj['min'])
                    if 'max' in obj:
                        q_label_object &= Q(submission_scores__score__lte=obj['max'])

                q_or_objects |= q_label_object

        # Combine: Dates AND (Label A OR Label B)
        # Only include or objects if filters are present to avoid potentially appending falsey value or unneeded joins
        q_final = q_and_objects
        if has_label_filters:
            q_final &= q_or_objects

        queryset = queryset.filter(q_final).distinct().order_by('-id')
        return PLIPSubmissionSerializer.setup_eager_loading(queryset)

    @extend_schema(responses={200: PLIPSubmissionSerializer})
    def post(self, request):
        queryset = self.get_queryset()
        page_size = 10
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(queryset, request)
        output_serializer = PLIPSubmissionSerializer(result_page, many=True)

        return paginator.get_paginated_response(output_serializer.data)


class PLIPAPICreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsContributor)
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = PLIPAPICreateSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = self.serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        input_file = input_serializer.validated_data.get('image', None)
        input_labels = input_serializer.validated_data.get('labels', None)

        try:
            file_content = input_file.read()
            md5_checksum = hashlib.md5(file_content).hexdigest()
            image_bin = io.BytesIO(file_content)
            pil_img = Image.open(image_bin).convert('RGB')

            if input_labels:
                labels = [label.strip() for label in input_labels.split(',')]

            else:
                labels = ["adipose", "background", "debris", "lymphocytes", "mucus", "smooth muscle",
                          "normal colon mucosa",
                          "cancer-associated stroma", "colorectal adenocarcinoma epithelium"]

            plip_classifier = PLIPClassifier()
            prediction = plip_classifier.predict(pil_img, candidate_labels=labels)

            results_sorted = dict(sorted(prediction['detailed_scores'].items(), key=lambda item: item[1], reverse=True))

            pil_img.thumbnail((224, 224), Image.Resampling.LANCZOS)
            thumb_buffer = io.BytesIO()
            pil_img.save(thumb_buffer, format="JPEG")

            # Execute statements with atomicity to ensure no partial relationships are created
            with transaction.atomic():
                # Only one instance of an image file is needed, so retrieve based on md5 if it exists, otherwise create
                image_obj, created = PLIPImage.objects.get_or_create(
                    md5=md5_checksum,
                    defaults={"blob_image": thumb_buffer.getvalue()},
                )

                # If expected_label is populated, get or create it as a label object
                expected_label_obj = None
                expected_label = input_serializer.validated_data.get('expected_label', None)

                if expected_label:
                    expected_label_obj, created = PLIPLabel.objects.get_or_create(
                        label=expected_label
                    )

                submission_obj = PLIPSubmission.objects.create(filename=input_file.name, image=image_obj,
                                                               expected_label=expected_label_obj,
                                                               user=self.request.user)

                for key, value in results_sorted.items():
                    label_obj, created = PLIPLabel.objects.get_or_create(
                        label=key
                    )

                    PLIPScore.objects.create(
                        label=label_obj,
                        score=value,
                        submission=submission_obj,
                    )

                queryset = PLIPSubmissionSerializer.setup_eager_loading(PLIPSubmission.objects.all())
                submission_obj = queryset.get(id=submission_obj.id)

            output_serializer = PLIPSubmissionSerializer(submission_obj)

            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Error processing image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
