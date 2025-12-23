from django.shortcuts import redirect

def set_theme(request):
    # Set dark/light theme in session, defaults to light
    theme = request.GET.get('theme', 'light')
    request.session['theme'] = theme
    # Redirect back to the previous page after toggle, or home if no referrer
    return redirect(request.META.get('HTTP_REFERER', '/'))
