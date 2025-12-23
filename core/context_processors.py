def theme_processor(request):
    # Dark/light theme processor
    return {'theme': request.session.get('theme', 'light')}