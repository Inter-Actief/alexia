from django.db import models
from django.db.models.query_utils import Q


class EventManager(models.Manager):
    """Provides several extra handy methods to find events."""

    def occuring_at(self, start, end):
        """Returns the events that occur (partially or entirely) between the
        given start and end datetimes.
        """
        # An event is in the given interval if the event's start or end date
        # is in the given interval, or when the start date is before the given
        # interval and the end date is after the given interval.
        #
        #        START  --------------------------------- END
        #                                       o----------------
        #    --------------o
        #    o--------------------------------------------------o
        return self.get_queryset() \
            .filter(
            # start < start_date < end
            (Q(starts_at__gt=start) & Q(starts_at__lt=end)) |
            # start < end_date < end
            (Q(ends_at__gt=start) & Q(ends_at__lte=end)) |
            # start <= start_date & end_date => end
            (Q(starts_at__lte=start) & Q(ends_at__gte=end)))
