from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from alexia.apps.scheduling.models import Event
from alexia.auth.decorators import tender_required


def _get_product_list(event):
    products = []

    for sellingprice in event.pricegroup.sellingprice_set.all():
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

    for product in event.temporaryproducts.all():
        products.append({
            'id': product.pk,
            'name': product.name,
            'text_color': product.text_color,
            'background_color': product.background_color,
            'price': int(product.price * 100),
        })

    return products


@login_required
@tender_required
def juliana(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if not event.is_tender(request.user):
        return render(request, '403.html', {'reason': _('You are not a tender for this event')}, status=403)
    if not event.can_be_opened(request.user):
        return render(request, '403.html', {'reason': _('This event is not open')}, status=403)

    products = _get_product_list(event)
    debug = settings.DEBUG
    countdown = settings.JULIANA_COUNTDOWN if hasattr(settings, 'JULIANA_COUNTDOWN') else 5
    androidapp = request.META.get('HTTP_X_REQUESTED_WITH') == 'net.inter_actief.juliananfc'

    return render(request, 'juliana/index.html', locals())
