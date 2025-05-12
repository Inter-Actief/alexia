def is_ajax(request):
    """
    Copied from Django because HttpRequest.is_ajax() was deprecated in 3.1 and removed in 4.x
    See: https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpRequest.is_ajax
    and: https://docs.djangoproject.com/en/3.2/_modules/django/http/request/#HttpRequest.is_ajax
    """
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
