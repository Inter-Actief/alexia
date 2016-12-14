import mimetypes

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from alexia.utils import log
from alexia.auth.backends import RADIUS_BACKEND_NAME
from alexia.auth.decorators import manager_required

from .forms import (
    CreateUserForm, MembershipAddForm, MembershipEditForm, UploadIvaForm,
)
from .models import AuthenticationData, Membership, Profile


@login_required
@manager_required
def membership_list(request):
    memberships = request.organization.membership_set.select_related('user').order_by('user__first_name')
    return render(request, 'membership/list.html', locals())


@login_required
@manager_required
def iva_list(request):
    memberships = request.organization.membership_set \
        .filter(is_tender=True).select_related('user').order_by('user__first_name')
    return render(request, 'membership/iva_list.html', locals())


@login_required
@manager_required
def membership_add(request):
    if request.method == 'POST':
        form = MembershipAddForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                authentication_data = AuthenticationData.objects.get(username=username, backend=RADIUS_BACKEND_NAME)
            except AuthenticationData.DoesNotExist:
                return redirect(membership_create_user, username=username)

            user = authentication_data.user
            membership, is_new = Membership.objects.get_or_create(user=user, organization=request.organization)
            if is_new:
                log.membership_created(request.user, membership)
            return redirect(membership_edit, pk=membership.pk)
    else:
        form = MembershipAddForm()

    return render(request, 'membership/form.html', locals())


@login_required
@manager_required
def membership_create_user(request, username):
    try:
        AuthenticationData.objects.get(username=username, backend=RADIUS_BACKEND_NAME)
        # Account already exists
        raise Http404
    except AuthenticationData.DoesNotExist:
        pass

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = username
            user.set_unusable_password()
            user.save()

            data = AuthenticationData(user=user, backend=RADIUS_BACKEND_NAME, username=username)
            data.save()

            profile = Profile(user=user)
            profile.save()

            membership, is_new = Membership.objects.get_or_create(user=user, organization=request.organization)
            if is_new:
                log.membership_created(request.user, membership)
            return redirect(membership_edit, pk=membership.pk)
    else:
        form = CreateUserForm(initial={'username': username})

    return render(request, 'membership/create_user.html', locals())


@login_required
@manager_required
def membership_show(request, pk):
    membership = get_object_or_404(Membership, pk=pk)

    if membership.organization != request.organization:
        raise PermissionDenied

    last_10_tended = membership.tended().order_by('-event__starts_at')[:10]
    is_planner = request.user.is_superuser or request.user.profile.is_planner(request.organization)

    from datetime import date
    from dateutil.relativedelta import relativedelta
    # Dates of all tended drinks in the last year.
    _last_year = (date.today()-relativedelta(years=1, day=1))
    _tended_dates = membership.tended().filter(event__starts_at__gte=_last_year).values_list('event__starts_at')

    # Change from list of 1-tuples to just a list of elements
    _tended_dates = [i[0] for i in _tended_dates]

    # Group by month
    _graph_data = {}
    for d in _tended_dates:
        if d.strftime("%Y-%m") in _graph_data.keys():
            _graph_data[d.strftime("%Y-%m")] += 1
        else:
            _graph_data[d.strftime("%Y-%m")] = 1

    # Fill in 0 for the missing months
    _date = date.today()
    while _last_year <= _date:
        if _date.strftime("%Y-%m") not in _graph_data.keys():
            _graph_data[_date.strftime("%Y-%m")] = 0
        _date -= relativedelta(months=1)

    graph_headers = sorted(_graph_data.keys())
    graph_content = [_graph_data[k] for k in graph_headers]

    return render(request, 'membership/show.html', locals())


@login_required
@manager_required
def membership_edit(request, pk):
    membership = get_object_or_404(Membership, pk=pk)

    if membership.organization != request.organization:
        raise PermissionDenied

    if request.method == 'POST':
        form = MembershipEditForm(request.POST, instance=membership)
        if form.is_valid():
            membership = form.save()
            log.membership_modified(request.user, membership)
            return redirect(membership)
    else:
        form = MembershipEditForm(instance=membership)

    return render(request, 'membership/form.html', locals())


@login_required
@manager_required
def membership_delete(request, pk):
    membership = get_object_or_404(Membership, pk=pk)

    if membership.organization != request.organization:
        raise PermissionDenied

    if request.method == 'POST':
        membership.delete()
        log.membership_deleted(request.user, membership)
        return redirect(membership_list)
    else:
        return render(request, 'membership/delete.html', locals())


@login_required
@manager_required
def membership_iva(request, pk):
    membership = get_object_or_404(Membership, pk=pk)

    if membership.organization != request.organization:
        raise PermissionDenied

    iva_file = membership.user.certificate.file
    content_type, encoding = mimetypes.guess_type(iva_file.url)
    content_type = content_type or 'application/octet-stream'
    return HttpResponse(iva_file, content_type=content_type)


@login_required
@manager_required
def iva_upload(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    if membership.organization != request.organization:
        raise PermissionDenied

    certificate = getattr(membership.user, 'certificate', None)
    if request.method == 'POST':
        form = UploadIvaForm(request.POST, request.FILES, instance=certificate)
        if form.is_valid():
            if certificate:
                certificate.delete()
            certificate = form.save(commit=False)
            certificate.owner_id = membership.user.pk
            certificate.save()
            return redirect(membership_list)
    else:
        form = UploadIvaForm(instance=certificate)

    return render(request, 'membership/iva_upload.html', locals())


@login_required
@manager_required
def iva_approve(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    certificate = membership.user.certificate

    if membership.organization != request.organization:
        raise PermissionDenied

    if certificate and not certificate.approved_at:
        certificate.approve(request.user)
        return redirect(membership_list)


@login_required
@manager_required
def iva_decline(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    certificate = membership.user.certificate

    if membership.organization != request.organization:
        raise PermissionDenied

    if certificate and not certificate.approved_at:
        certificate.decline()
        return redirect(membership_list)
