import hashlib
import mimetypes
import random

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from apps.billing.models import Order
from utils.auth.decorators import tender_required
from .forms import ProfileForm, IvaForm


@login_required
def index(request):
    order_list = Order.objects.select_related('event').filter(
        authorization__in=request.user.authorizations.all())
    order_count = len(order_list)
    orders = order_list.order_by('-placed_at')[:5]
    return render(request, 'profile/index.html', locals())


@login_required
@tender_required
def ical_gen(request):
    seed = random.randint(1, 10000)
    request.user.profile.ical_id = hashlib.md5("%s%s" % (request.user.username,
                                                         seed)).hexdigest()
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
    profile = request.user.profile
    certificate = profile.certificate

    if request.method == 'POST':
        form = IvaForm(request.POST, request.FILES)
        if form.is_valid():
            # Delete the old
            if certificate:
                certificate.delete()
            # Save the new
            certificate = form.save(commit=False)
            certificate._id = str(profile.user.pk)
            certificate._radius = profile.radius_username
            certificate.save()
            # Attach to profile
            profile.certificate = certificate
            profile.save()

            return redirect(index)
    else:
        form = IvaForm(instance=certificate)

    return render(request, 'profile/iva.html', locals())


@login_required
def view_iva(request):
    if not request.user.profile.certificate:
        raise Http404

    iva_file = request.user.profile.certificate.file
    content_type, encoding = mimetypes.guess_type(iva_file.url)
    content_type = content_type or 'application/octet-stream'
    return HttpResponse(iva_file, content_type=content_type)


@login_required
def payments(request):
    order_list = Order.objects.filter(
        authorization__in=request.user.authorizations.all()) \
        .order_by('-placed_at')
    paginator = Paginator(order_list, 25)

    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    return render(request, 'profile/payments.html', locals())
