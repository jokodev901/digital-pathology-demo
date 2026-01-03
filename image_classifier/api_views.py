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
from rest_framework.reverse import reverse
from rest_framework.pagination import PageNumberPagination

from .models import PLIPSubmission, PLIPImage, PLIPLabel, PLIPScore
from .serializers.plip_serializers import PLIPAPIListSerializer, PLIPAPIInputSerializer, PLIPAPIOutputSerializer, PLIPSubmissionSerializer
from .services.plip import PLIPClassifier


class PLIPAPIListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PLIPAPIListSerializer

    def get_queryset(self):
        queryset = (PLIPSubmission.objects.select_related('image').all()
                    .prefetch_related('submission_scores__label').order_by('-id'))

        q_and_objects = Q()
        q_or_objects = Q()

        if 'min_date' in self.request.data:
            q_and_objects &= Q(created_at__gte=self.request.data['min_date'])

        if 'max_date' in self.request.data:
            q_and_objects &= Q(created_at__lte=self.request.data['max_date'])

        if 'labels' in self.request.data:
            for obj in self.request.data['labels']:
                q_label_object = Q()
                if 'label' in obj:
                    q_label_object &= Q(submission_scores__label__label__icontains=obj['label'])
                    if 'min' in obj:
                        q_label_object &= Q(submission_scores__score__gte=obj['min'])
                    if 'max' in obj:
                        q_label_object &= Q(submission_scores__score__lte=obj['max'])

                q_or_objects |= q_label_object

        q_final = q_and_objects & q_or_objects
        queryset = queryset.filter(q_final)

        return queryset

    def post(self, request):
        queryset = self.get_queryset()
        page_size = 10
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(queryset, request)
        output_serializer = PLIPAPIOutputSerializer(result_page, many=True)

        return paginator.get_paginated_response(output_serializer.data)


class PLIPAPICreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, )
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = PLIPAPIInputSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        input_file = input_serializer.validated_data['image']
        input_labels = input_serializer.validated_data['labels']

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

                submission_obj = PLIPSubmission.objects.create(filename=input_file.name,
                                                               image=image_obj, user=self.request.user)

                for key, value in results_sorted.items():
                    label_obj, created = PLIPLabel.objects.get_or_create(
                        label=key
                    )

                    PLIPScore.objects.create(
                        label=label_obj,
                        score=value,
                        submission=submission_obj,
                    )

                submission_obj = (
                    PLIPSubmission.objects.select_related('image')
                    .prefetch_related('submission_scores__label')
                    .get(id=submission_obj.id)
                )

            output_serializer = PLIPAPIOutputSerializer(submission_obj)

            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Error processing image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class APIRootView(APIView):
    """
    Root API index
    Lists all available endpoints
    """
    def get(self, request, format=None):
        return Response({
            'pliplist': reverse('plip-list', request=request, format=format),
            'plipinput': reverse('plip-input', request=request, format=format),
        })
