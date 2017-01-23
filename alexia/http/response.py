from django.http import HttpResponse


class IcalResponse(HttpResponse):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('content_type', 'text/calendar')
        super(IcalResponse, self).__init__(*args, **kwargs)
