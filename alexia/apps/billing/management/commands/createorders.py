import random

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone

from alexia.apps.billing.models import Order, PermanentProduct, Purchase
from alexia.apps.scheduling.models import Event


class Command(BaseCommand):
    help = 'Create some dummy orders for testing'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('This command only runs if DEBUG is True.')

        if len(args) < 2:
            raise CommandError('This command requires an event id and a number of orders.')

        try:
            event_pk = int(args[0])
        except ValueError:
            raise CommandError('First argument is not an integer.')

        try:
            order_count = int(args[1])
        except ValueError:
            raise CommandError('Second argument is not an integer.')

        try:
            event = Event.objects.get(pk=event_pk)
        except Event.DoesNotExist:
            raise CommandError('Event not found.')

        organizer = event.organizer

        now = timezone.now()
        authorizations = organizer.authorizations.filter(Q(end_date__gte=now) | Q(end_date__isnull=True),
                                                         start_date__lte=now)

        user = User.objects.get(id=1)

        if not authorizations:
            raise CommandError('No active authorizations for organizer.')

        products = PermanentProduct.objects.filter(productgroup__pricegroups__events=event)

        for i in range(order_count):
            print('-----')
            product_count = random.randint(1, 10)
            print('%s products' % product_count)

            order = Order(event=event, authorization=random.choice(authorizations), added_by=user)
            order.save()

            for j in range(product_count):
                product = random.choice(products)
                amount = random.randint(1, 10)
                price = amount * product.get_price(event)

                purchase = Purchase(order=order, product=product, amount=amount, price=price)
                purchase.save()
