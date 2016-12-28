from django.db import models
from django.db.models import Q


class EventManager(models.Manager):
    def occuring_at(self, start, end):
        # An event is in the given interval if the event's start or end date
        # is in the given interval, or when the start date is before the given
        # interval and the end date is after the given interval.
        #
        #        START  --------------------------------- END
        #                                       o----------------
        #    --------------o
        #    o--------------------------------------------------o
        return self.get_queryset().filter(
            (Q(starts_at__gt=start) & Q(starts_at__lt=end)) |  # start < start_date < end
            (Q(ends_at__gt=start) & Q(ends_at__lte=end)) |     # start < end_date < end
            (Q(starts_at__lte=start) & Q(ends_at__gte=end))    # start <= start_date & end_date => end
        )
