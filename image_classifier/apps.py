from django.apps import AppConfig


class ImageClassifierConfig(AppConfig):
    name = 'image_classifier'

    def ready(self):
        try:
            from .services.plip import PLIPClassifier
            PLIPClassifier()
        except Exception as e:
            print(f"Could not ready PLIPClassifier {e}")