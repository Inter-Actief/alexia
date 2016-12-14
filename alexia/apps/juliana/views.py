from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.generic.detail import DetailView
from django.utils.translation import ugettext_lazy as _

from alexia.apps.scheduling.models import Event
from alexia.auth.mixins import TenderRequiredMixin


class JulianaView(TenderRequiredMixin, DetailView):
    template_name = 'juliana.html'
    model = Event

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.is_tender(request.user):
            raise PermissionDenied(_('You are not a tender for this event'))
        if not self.object.can_be_opened(request.user):
            raise PermissionDenied(_('This event is not open'))

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(JulianaView, self).get_context_data(**kwargs)
        context.update({
            'products': self.get_product_list(),
            'debug': settings.DEBUG,
            'countdown': settings.JULIANA_COUNTDOWN if hasattr(settings, 'JULIANA_COUNTDOWN') else 5,
            'androidapp': self.request.META.get('HTTP_X_REQUESTED_WITH') == 'net.inter_actief.juliananfc',
        })
        return context

    def get_product_list(self):
        products = []

        for sellingprice in self.object.pricegroup.sellingprice_set.all():
            for product in sellingprice.productgroup.permanentproduct_set.all():
                products.append({
                    'id': product.pk,
                    'name': product.name,
                    'text_color': product.text_color,
                    'background_color': product.background_color,
                    'price': int(sellingprice.price * 100),
                    'position': product.position,
                })

        products.sort(key=lambda x: x['position'])

        for product in self.object.temporaryproducts.all():
            products.append({
                'id': product.pk,
                'name': product.name,
                'text_color': product.text_color,
                'background_color': product.background_color,
                'price': int(product.price * 100),
            })

        return products
