from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


def set_theme(request):
    # Set dark/light theme in session, defaults to dark
    theme = request.GET.get('theme', 'dark')
    request.session['theme'] = theme
    # Redirect back to the previous page after toggle, or home if no referrer
    return redirect(request.META.get('HTTP_REFERER', '/'))


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'