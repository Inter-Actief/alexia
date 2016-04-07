from alexia.stock.forms import StockCountForm, StockCountAmountForm, StockProductForm
from alexia.stock.models import Event
from alexia.stock.models import StockProductAmount, StockProduct, \
    StockCount
from alexia.tools.decorators import manager_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render_to_response, RequestContext
from django.utils import timezone


@manager_required
def stock_list(request):
    stockproducts = StockProduct.objects.all()
    stock = {}

    for stockproduct in stockproducts:
        stock[stockproduct] = stockproduct.in_stock()

    return render_to_response('stock_list.html', locals(), RequestContext(request))


@manager_required
def edit_stockcount(request, stockcount_id=None):
    products = StockProduct.objects.all().order_by('pk')
    if request.method == "POST":
        scform = StockCountForm(data=request.POST)
        scaforms = [StockCountAmountForm(data=request.POST, prefix=x.pk) for x in products]

        if scform.is_valid() and any([scaform.is_valid() for scaform in
                                      scaforms]):

            stockcount = scform.save(commit=False)
            stockcount.organization = request.organization
            stockcount.user = request.user
            stockcount.date = timezone.now()
            stockcount.is_completed = True
            stockcount.save()

            for scaform in scaforms:
                if scaform.is_valid():
                    prod = StockProduct.objects.get(pk=scaform.cleaned_data['product_id'])
                    sca = StockProductAmount.objects.get_or_create(stockcount=stockcount, product=prod,
                                                                   amount=scaform.cleaned_data['amount'])

            return render(request, 'closepopup.html', {})

    else:
        if stockcount_id:
            stockcount = StockCount.objects.get(pk=stockcount_id)
            scform = StockCountForm(instance=stockcount)
        else:
            scform = StockCountForm()
        scaforms = [StockCountAmountForm(product=x, prefix=x.pk) for x in products]

    return render(request, 'stocking/stockcountform.html', {'scform': scform,
                                                            'scaforms': scaforms})


@manager_required
def edit_stockproduct(request, product_id=None):
    if product_id:
        product = get_object_or_404(StockProduct, id=product_id)
    else:
        product = None
    if request.method == "POST":
        spform = StockProductForm(data=request.POST, instance=product)
        if spform.is_valid():
            spform.save()
            return render(request, 'closepopup.html', {})
    else:
        spform = StockProductForm(instance=product)

    return render(request, 'stocking/edit_stockproduct.html', {'spform': spform, 'stockproduct': product})


def list_event_consumptions(request, event_id):
    event = Event.objects.get(id=event_id)
    event_consumptions = event.eventconsumption_set.all()

    return render(request, 'stocking/event_consumption_list.html',
                  {'event': event, 'event_consumptions': event_consumptions})


@login_required
def new(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if not event.can_edit_event_consumptions():
        # hier afhandelen dat de gebruiker dit niet meer mag
        return render(request, 'stocking/event_consumption_closed_message.html', {})

    if request.method == "POST":
        form = EventConsumptionForm(event=event, data=request.POST)

        if form.is_valid():
            form.save()
            return render(request, 'closepopup.html', {})

    else:
        form = EventConsumptionForm(event=event)

    return render(request, 'stocking/event_consumption_form.html', {'form': form})


def open(request, event_id, event_consumption_id):
    # TODO: Permissies checken!!
    return render(request, 'stocking/event_consumption_open.html', {})
