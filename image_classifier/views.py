import io
import base64
import tempfile

from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from PIL import Image
from .forms import ImageUploadForm
from .services.plip import PLIPClassifier


class PLIPView(LoginRequiredMixin, FormView):
    template_name = 'plip.html'
    form_class = ImageUploadForm

    def form_valid(self, form):
        uploaded_file = self.request.FILES['image']
        form_labels = form.cleaned_data['labels']

        if form_labels:
            labels = form_labels.split(',')

        else:
            labels = ["adipose", "background", "debris", "lymphocytes", "mucus", "smooth muscle", "normal colon mucosa",
                      "cancer-associated stroma", "colorectal adenocarcinoma epithelium"]

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

            temp_path = temp_file.name

        pil_img = Image.open(temp_path).convert('RGB')
        plip_classifier = PLIPClassifier()
        prediction = plip_classifier.predict(pil_img, candidate_labels=labels)

        # Save resized image file for output with results
        pil_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        results_sorted = dict(sorted(prediction['detailed_scores'].items(), key=lambda item: item[1], reverse=True))
        results_rounded = ', '.join([f"{key}: {round(value, 2)}" for key, value in results_sorted.items()])

        # Re-render the page with the result
        return self.render_to_response(
            self.get_context_data(form=form, result=results_rounded, thumbnail=image_base64)
        )
