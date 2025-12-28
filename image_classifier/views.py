import io
import base64
import numpy as np

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

        if uploaded_file:
            pil_img = Image.open(uploaded_file).convert('RGB')
            pil_img.thumbnail((400, 400), Image.Resampling.LANCZOS)

            # Save resized image file for output with results
            buffer = io.BytesIO()
            pil_img.save(buffer, format="JPEG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            patch = np.array(pil_img)
            plip_classifier = PLIPClassifier()

            prediction = plip_classifier.predict(patch, candidate_labels=labels)
            result = f"{prediction['predicted_label']} {prediction['confidence']:.4f}"

        else:
            result = "No file uploaded"
            image_base64 = None

        # Re-render the page with the result
        return self.render_to_response(
            self.get_context_data(form=form, result=result, thumbnail=image_base64)
        )
