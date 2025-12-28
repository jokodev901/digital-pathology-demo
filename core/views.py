import json
from pathlib import Path
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


# Import apps.json for building app cards on the home page
# app card data is cached and built out once at django web service start
def load_apps(path):
    with open(path, 'r') as f:
        return json.load(f)

JSON_PATH = Path(settings.BASE_DIR) / 'core' / 'data' / 'apps.json'
APPS_CACHE = load_apps(JSON_PATH)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apps'] = APPS_CACHE
        return context