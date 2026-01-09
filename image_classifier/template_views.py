import io
import tempfile
import hashlib

from PIL import Image

from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.views import View
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from authentication.permissions import ContributorRequiredMixin
from .forms import ImageUploadForm
from .services.plip import PLIPClassifier
from .models import PLIPImage, PLIPSubmission, PLIPLabel, PLIPScore
from .serializers.plip_serializers import PLIPSubmissionSerializer


class AddFilterRowView(LoginRequiredMixin, View):
    def get(self, request):
        current_index = int(request.GET.get('current_index', 0))
        return render(request, '_filter_row.html', {
            'index': current_index + 1
        })


class UpdateFilterStateView(LoginRequiredMixin, View):
    """
    Control PLIP filter window open/collapsed state
    """
    def get(self, request):
        state = request.GET.get('state')
        request.session['filters_expanded'] = (state == 'open')
        # Explicitly mark the session as modified to ensure it's saved to the DB/Cache
        request.session.modified = True
        return HttpResponse(status=204)


class PLIPView(LoginRequiredMixin, ContributorRequiredMixin, FormView):
    template_name = 'plip.html'
    form_class = ImageUploadForm

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['image']
        form_labels = form.cleaned_data['labels']
        expected_label = form.cleaned_data['expected_label']
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
            labels = [label.strip() for label in form_labels.split(',')]

        else:
            labels = ["adipose", "background", "debris", "lymphocytes", "mucus", "smooth muscle", "normal colon mucosa",
                      "cancer-associated stroma", "colorectal adenocarcinoma epithelium"]

        prediction = plip_classifier.predict(pil_img, candidate_labels=labels)

        # Sort results and create clean string of rounded values for output
        results_sorted = dict(sorted(prediction['detailed_scores'].items(), key=lambda item: item[1], reverse=True))
        results_str = '<br>'.join([f"{key}: {round(value, 2)}" for key, value in results_sorted.items()])

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

            if expected_label:
                expected_label_obj, created = PLIPLabel.objects.get_or_create(
                    label=expected_label
                )

            submission_obj = PLIPSubmission.objects.create(filename=uploaded_file.name, image=image_obj,
                                                           expected_label=expected_label_obj, user=self.request.user)

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
            self.get_context_data(form=form, result=results_str, expected_label=expected_label,
                                  thumbnail=image_obj.image_base64)
        )


class PLIPImageView(LoginRequiredMixin, TemplateView):
    template_name = 'plip_data_browser.html'
    page_size = 10

    def get_queryset(self):
        queryset = (PLIPSubmission.objects.select_related('image').all()
                    .prefetch_related('submission_scores__label').order_by('-id'))

        q_and_objects = Q()
        q_or_objects = Q()

        has_label_filters = False

        # min_date = self.request.GET.get('min_date')
        # max_date = self.request.GET.get('max_date')
        #
        # if min_date:
        #     q_and_objects &= Q(created_at__gte=min_date)
        # if max_date:
        #     q_and_objects &= Q(created_at__lte=max_date)

        # Expected label filter
        expected = self.request.GET.get('expected')
        if expected:
            q_and_objects &= Q(expected_label__label__iexact=expected)

        # Dynamic Label Filters (label_0 ... label_4)
        for i in range(5):
            label = self.request.GET.get(f'label_{i}')
            min_score = self.request.GET.get(f'min_{i}')
            max_score = self.request.GET.get(f'max_{i}')

            if label:
                has_label_filters = True
                q_label_object = Q(submission_scores__label__label__icontains=label)

                if min_score:
                    q_label_object &= Q(submission_scores__score__gte=float(min_score))
                if max_score:
                    q_label_object &= Q(submission_scores__score__lte=float(max_score))

                # Multiple label/score filters are evaluated as ORs
                q_or_objects |= q_label_object

        # Combine: Dates AND (Label A OR Label B)
        # Only include or objects if filters are present to avoid potentially appending falsey value or unneeded joins
        q_final = q_and_objects
        if has_label_filters:
            q_final &= q_or_objects

        return queryset.filter(q_final).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters_expanded'] = self.request.session.get('filters_expanded', True)

        # Get Filtered Data
        filtered_qs = self.get_queryset()

        # Paginate results
        paginator = Paginator(filtered_qs, self.page_size)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)

        # Serialize page
        serialized_submissions = PLIPSubmissionSerializer(page, many=True).data
        for submission in serialized_submissions:
            scores_list = []
            for score in submission['submission_scores']:
                scores_list.append(f"{score['label']}: {score['rounded_score']}")
            submission['scores_str'] = '<br>'.join(scores_list)

        context['submissions'] = serialized_submissions

        # Construct Pagination object
        context['pagination'] = {
            'number': page.number,
            'num_pages': paginator.num_pages,
            'has_next': page.has_next,
            'has_previous': page.has_previous,
            'next_page_number': page.next_page_number if page.has_next() else None,
            'previous_page_number': page.previous_page_number if page.has_previous() else None
        }

        # Identify existing filter indices for persistence after "apply filters"
        # active_indices = set([0])  # Always include row 0
        active_indices = {0}
        for key in self.request.GET.keys():
            if key.startswith('label_'):
                try:
                    # Extract '3' from 'label_3'
                    index = int(key.split('_')[1])
                    active_indices.add(index)
                except (ValueError, IndexError):
                    continue

        # Extract existing filters from request and populate
        filter_rows = []
        for i in sorted(list(active_indices)):
            filter_rows.append({
                'index': i,
                'label': self.request.GET.get(f'label_{i}', ''),
                'expected': self.request.GET.get(f'expected_{i}', ''),
                # 'min': self.request.GET.get(f'min_{i}', ''),
                # 'max': self.request.GET.get(f'max_{i}', ''),
            })

        context['filter_rows'] = filter_rows

        # Preserve URL params
        params = self.request.GET.copy()
        if 'page' in params:
            del params['page']
        context['url_params'] = params.urlencode()

        return context
