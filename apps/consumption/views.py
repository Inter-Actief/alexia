from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from apps.scheduling.models import Event


def dcf(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if not event.is_tender(request.user):
        return render(request, '403.html', {'reason': _('You are not a tender for this event')}, status=403)

    return render(request, 'consumption/dcf.html', locals())
