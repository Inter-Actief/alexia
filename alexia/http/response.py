from django.http import HttpResponse


class IcalResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        kwargs.setdefault('content_type', 'text/calendar')
        data = data.to_ical()
        super(IcalResponse, self).__init__(content=data, **kwargs)
