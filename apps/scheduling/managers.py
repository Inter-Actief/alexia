from datetime import timedelta

from django.db import models
from django.db.models.query_utils import Q


class EventManager(models.Manager):
    """Provides several extra handy methods to find events."""
    def get_queryset(self):
        return super(EventManager, self).get_queryset().filter(deleted=False)

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
            (Q(starts_at__gt=start) & Q(starts_at__lt=end))
            # start < end_date < end
            | (Q(ends_at__gt=start) & Q(ends_at__lte=end))
            # start <= start_date & end_date => end
            | (Q(starts_at__lte=start) & Q(ends_at__gte=end)))


class StandardReservationManager(models.Manager):
    def occuring_at(self, start, end):
        start_day = start.isoweekday()
        start_time = start.time()
        end_day = end.isoweekday()
        end_time = end.time()

        # Case I: the event takes more then one week: all reservations are
        # conflicting
        if (end - start) > timedelta(weeks=1):
            return self.get_queryset().all()

        # The end day is before the start day. This means that we got through
        # sunday, and we just split up the result.
        elif end_day < start_day:
            monday0am = (end - timedelta(days=(end_day - 1))).replace(
                hour=0, minute=0, second=0, microsecond=0)
            return (self.occuring_at(start, monday0am - timedelta(seconds=1)) |
                    self.occuring_at(monday0am, end))

        # No special case, we just have to
        else:
            return self.get_queryset() \
                .filter(
                ((Q(start_day=start_day) & Q(start_time__gt=start_time)
                  | Q(start_day__gt=start_day))  # db.start > ob.start
                 & (Q(start_day=end_day) & Q(start_time__lt=end_time)
                    | Q(start_day__lt=end_day)))  # db.start < ob.end
                | ((Q(end_day=start_day) & Q(end_time__gt=start_time)
                    | Q(end_day__gt=start_day))  # db.end > ob.start
                   & (Q(end_day=end_day) & Q(end_time__lt=end_time)
                      | Q(end_day__lt=end_day)))  # db.end < ob.end
                | ((Q(start_day=start_day) & Q(start_time__lt=start_time)
                    | Q(start_day__lt=start_day))  # db.start < ob.start
                   & (Q(end_day=end_day) & Q(end_time__gt=end_time)
                      | Q(end_day__gt=end_day)))  # db.end > ob.end
            )
