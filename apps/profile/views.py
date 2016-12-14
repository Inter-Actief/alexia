import mimetypes
import uuid

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

from apps.billing.models import Order
from apps.organization.models import AuthenticationData
from apps.scheduling.models import Event
from utils.auth.backends import RADIUS_BACKEND_NAME
from utils.auth.decorators import tender_required

from .forms import IvaForm, ProfileForm


@login_required
def index(request):
    event_list = Event.objects.filter(orders__authorization__in=request.user.authorizations.all()) \
                              .annotate(spent=Sum('orders__amount'))
    event_count = event_list.count()
    events = event_list.order_by('-ends_at')[:5]

    order_count = Order.objects.select_related('event').filter(
        authorization__in=request.user.authorizations.all()).count()

    shares = []
    for authorization in request.user.authorizations.all():
        my_order_sum = Order.objects.filter(authorization=authorization).aggregate(total=Sum('amount'))
        all_order_sum = Order.objects.filter(authorization__organization=authorization.organization) \
            .aggregate(total=Sum('amount'))

        if not my_order_sum['total'] or not all_order_sum['total']:
            percentage = 0
        else:
            percentage = (my_order_sum['total'] / all_order_sum['total']) * 100

        shares.append({'organization': authorization.organization, 'percentage': round(percentage, 2)})

    try:
        radius_username = request.user.authenticationdata_set.get(backend=RADIUS_BACKEND_NAME).username
    except AuthenticationData.DoesNotExist:
        radius_username = None

    return render(request, 'profile/index.html', locals())


@login_required
@tender_required
def ical_gen(request):
    request.user.profile.ical_id = uuid.uuid4()
    request.user.profile.save()
    return redirect(index)


@login_required
def edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(index)
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'profile/edit.html', {'form': form})


@login_required
def iva(request):
    certificate = getattr(request.user, 'certificate', None)

    if request.method == 'POST':
        form = IvaForm(request.POST, request.FILES)
        if form.is_valid():
            # Delete the old
            if certificate:
                certificate.delete()
            # Save the new
            certificate = form.save(commit=False)
            certificate._id = str(request.user.pk)
            certificate.save()
            # Attach to profile
            request.user.certificate = certificate
            request.user.save()

            return redirect(index)
    else:
        form = IvaForm(instance=certificate)

    return render(request, 'profile/iva.html', locals())


@login_required
def view_iva(request):
    if not request.user.certificate:
        raise Http404

    iva_file = request.user.certificate.file
    content_type, encoding = mimetypes.guess_type(iva_file.url)
    content_type = content_type or 'application/octet-stream'
    return HttpResponse(iva_file, content_type=content_type)


@login_required
def expenditures(request):
    event_list = Event.objects.filter(orders__authorization__in=request.user.authorizations.all()) \
                              .annotate(spent=Sum('orders__amount')) \
                              .order_by('-ends_at')
    paginator = Paginator(event_list, 25)

    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    return render(request, 'profile/expenditures.html', locals())


@login_required
def expenditures_event(request, pk):
    event = Event.objects.get(pk=pk)

    order_list = Order.objects.filter(
        authorization__in=request.user.authorizations.all(),
        event=pk).order_by('-placed_at')
    paginator = Paginator(order_list, 25)

    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    return render(request, 'profile/expenditures_event.html', locals())
