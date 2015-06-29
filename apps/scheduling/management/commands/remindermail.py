"""Tool voor het versturen van reminder-mails.

Deze tool verstuurt reminder-mails naar alle tappers met daarin een
lijst van borrels waarvan ze hun beschikbaarheid nog niet hebben
aangegeven.

Gebaseerd op de reminder-mails-script van Wietse Smid van het vorige
borrelbeheersysteem.

Auteur: Jelte Zeilstra
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.organization.models import Organization
from apps.scheduling.models import MailTemplate
from utils.mail import mail


class Command(BaseCommand):
    help = 'Send reminder mails for events with missing availabilities'

    def handle(self, *args, **options):
        # TODO: Setting / parameter van organization maken
        organizer = Organization.objects.get(name='Inter-Actief')

        memberships = organizer.membership_set.filter(is_tender=True)

        now = timezone.now()
        events = organizer.participates.filter(
            starts_at__gte=now, is_closed=False).order_by('starts_at', )

        # Load templates
        try:
            mailtemplate = MailTemplate.objects.get(
                organization=organizer, name="reminder")
        except MailTemplate.DoesNotExist:
            raise CommandError(
                'MailTemplate "reminder" does not exist for %s' % organizer)

        for membership in memberships:
            user = membership.user
            if not user.email:
                self.stderr.write('%s heeft geen e-mailadres.\n' % (user,))
                continue

            missing_events = events.exclude(
                pk__in=user.event_set.values_list('id', flat=True))
            addressees = [user]

            mail(settings.EMAIL_FROM, addressees, mailtemplate.subject,
                 mailtemplate.template,
                 extraattrs={'missing_events': missing_events, 'now': now})
