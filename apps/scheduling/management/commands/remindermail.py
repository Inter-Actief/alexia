"""
Command to send weekly reminder mails.

This tool sends reminder mails to all tenders with a list of events with
missing availability for the tender.

Based on the reminder script of the previous Event management system by
Wietse Smid.

Author: Jelte Zeilstra
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
        # Filter onganizations with an active reminder mail
        organizations = Organization.objects.filter(mailtemplate__name='reminder', mailtemplate__is_active=True)

        for organization in organizations:
            memberships = organization.membership_set.filter(is_tender=True)

            now = timezone.now()
            events = organization.participates.filter(starts_at__gte=now, is_closed=False).order_by('starts_at', )

            # Load templates
            try:
                mailtemplate = MailTemplate.objects.get(organization=organization, name="reminder", is_active=True)
            except MailTemplate.DoesNotExist:
                raise CommandError('MailTemplate "reminder" does not exist for %s' % organization)

            for membership in memberships:
                user = membership.user
                if not user.email:
                    self.stderr.write('%s heeft geen e-mailadres.\n' % (user,))
                    continue

                missing_events = events.exclude(pk__in=user.event_set.values_list('id', flat=True))
                addressees = [user]

                mail(settings.EMAIL_FROM, addressees, mailtemplate.subject, mailtemplate.template,
                     extraattrs={'missing_events': missing_events, 'now': now})
