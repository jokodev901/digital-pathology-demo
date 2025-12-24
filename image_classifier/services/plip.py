import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel


class PLIPClassifier:
    """
    A singleton service for Zero-Shot classification using the PLIP model.
    This ensures the heavy model is only loaded once into memory.torch
    """
    _instance = None
    _model = None
    _processor = None

    def __new__(cls):
        """Ensure only one class instance is instantiated at a time"""
        if cls._instance is None:
            cls._instance = super(PLIPClassifier, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):
        """Loads the vinid/plip model from Hugging Face."""
        try:
            model_id = "vinid/plip"

            # Check for GPU availability
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

            self._model = CLIPModel.from_pretrained(model_id).to(self.device)
            self._processor = CLIPProcessor.from_pretrained(model_id)
            self._model.eval()  # Set to evaluation mode

        except Exception as e:
            print(f"Failed to load PLIP model: {e}")
            raise

    def predict(self, image_input, candidate_labels=None):
        """
        Classifies a tissue patch against a list of text labels.

        Args:
            image_input (numpy.ndarray): The image patch (H, W, C) from Squidpy.
            candidate_labels (list[str]): List of tissue types to detect.

        Returns:
            dict: {'label': str, 'score': float, 'all_scores': dict}
        """
        if candidate_labels is None:
            candidate_labels = ["tumor tissue", "stroma", "lymphocytes", "normal tissue"]

        # 1. Preprocess Image
        # Squidpy/xarray often returns (Z, Y, X, C) or float types.
        # We ensure it's a standard uint8 PIL Image.
        try:
            if hasattr(image_input, 'values'):  # Handle xarray/squidpy objects
                image_input = image_input.values

            # Normalize dimensions if extra batch dim exists
            if image_input.ndim == 4:
                image_input = image_input[0]

            # Convert to PIL
            image_pil = Image.fromarray(np.uint8(image_input))
        except Exception as e:
            print(f"Image conversion failed: {e}")
            return {"error": "Invalid image format"}

        # 2. Process Inputs
        inputs = self._processor(
            text=candidate_labels,
            images=image_pil,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        # 3. Inference (No Gradient)
        with torch.no_grad():
            outputs = self._model(**inputs)

        # 4. Calculate Probabilities
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).cpu().numpy()[0]

        # 5. Format Results
        result_dict = {label: float(prob) for label, prob in zip(candidate_labels, probs)}
        best_idx = probs.argmax()

        return {
            "predicted_label": candidate_labels[best_idx],
            "confidence": float(probs[best_idx]),
            "detailed_scores": result_dict
        }