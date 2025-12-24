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

        if uploaded_file:
            pil_image = Image.open(uploaded_file).convert('RGB')
            patch = np.array(pil_image)
            plip_classifier = PLIPClassifier()

            # hardcoded for testing, will parameterize later
            labels = ["adipose", "background", "debris", "lymphocytes", "mucus", "smooth muscle", "normal colon mucosa",
                      "cancer - associated stroma", "colorectal adenocarcinoma epithelium"]

            prediction = plip_classifier.predict(patch, candidate_labels=labels)
            result = f"{prediction['predicted_label']} {prediction['confidence']:.4f}"

        else:
            result = "No file uploaded"

        # Re-render the page with the result
        return self.render_to_response(
            self.get_context_data(form=form, result=result)
        )
