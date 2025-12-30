import io
import tempfile
import hashlib

from PIL import Image

from django.core.paginator import Paginator
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ImageUploadForm
from .services.plip import PLIPClassifier
from .models import PLIPImage, PLIPSubmission, PLIPLabel, PLIPScore
from .serializers.plip_serializers import PLIPSubmissionSerializer, PLIPScoreSerializer


class PLIPView(LoginRequiredMixin, FormView):
    template_name = 'plip.html'
    form_class = ImageUploadForm

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['image']
        form_labels = form.cleaned_data['labels']
        md5 = hashlib.md5()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
                md5.update(chunk)

            temp_path = temp_file.name

        md5_checksum = md5.hexdigest()

        pil_img = Image.open(temp_path).convert('RGB')
        plip_classifier = PLIPClassifier()

        if form_labels:
            labels = form_labels.split(',')

        else:
            labels = ["adipose", "background", "debris", "lymphocytes", "mucus", "smooth muscle", "normal colon mucosa",
                      "cancer-associated stroma", "colorectal adenocarcinoma epithelium"]

        prediction = plip_classifier.predict(pil_img, candidate_labels=labels)

        # Sort results and create clean string of rounded values for output
        results_sorted = dict(sorted(prediction['detailed_scores'].items(), key=lambda item: item[1], reverse=True))
        results_str = ', '.join([f"{key}: {round(value, 2)}" for key, value in results_sorted.items()])

        pil_img.thumbnail((224, 224), Image.Resampling.LANCZOS)
        img_buffer = io.BytesIO()
        pil_img.save(img_buffer, format="JPEG")


        # Only one instance of an image file is needed, so retrieve based on md5 if it exists, otherwise create
        image_obj, created = PLIPImage.objects.get_or_create(
            md5=md5_checksum,
            defaults={"blob_image": img_buffer.getvalue()},
        )

        submission_obj = PLIPSubmission.objects.create(filename=uploaded_file.name, image=image_obj, user=self.request.user)

        for key, value in results_sorted.items():
            label_obj, created = PLIPLabel.objects.get_or_create(
                label=key
            )

            PLIPScore.objects.create(
                label=label_obj,
                score=value,
                submission=submission_obj,
            )

        # Re-render the page with the results
        return self.render_to_response(
            self.get_context_data(form=form, result=results_str, thumbnail=image_obj.image_base64)
        )


class PLIPImageView(LoginRequiredMixin, TemplateView):
    template_name = 'plip_data_browser.html'
    page_size = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission_queryset = PLIPSubmission.objects.select_related('image').all().prefetch_related('submission_scores__label').order_by('-id')

        paginator = Paginator(submission_queryset, self.page_size)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)

        pagination_data = {'number': page.number,
                           'num_pages': paginator.num_pages,
                           'has_next': page.has_next,
                           'has_previous': page.has_previous,
                           'next_page_number': page.next_page_number,
                           'previous_page_number': page.previous_page_number}

        serialized_submissions = PLIPSubmissionSerializer(page, many=True).data

        for submission in serialized_submissions:
            scores_list = []

            for score in submission['submission_scores']:
                scores_list.append(f"{score['label']['label']}: {score['rounded_score']}")

            submission['scores_str'] = '<br>'.join(scores_list)

        context['submissions'] = serialized_submissions
        context['pagination'] = pagination_data

        return context
