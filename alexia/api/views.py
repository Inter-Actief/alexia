from django.views.generic.base import TemplateView


class APIInfoView(TemplateView):
    template_name = 'api/info.html'
