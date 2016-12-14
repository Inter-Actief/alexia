from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from alexia.apps.organization.models import Organization
from alexia.apps.scheduling.models import MailTemplate
from alexia.utils.mail import mail


class Command(BaseCommand):
    help = 'Send reminder mails for events with missing availabilities'

    def handle(self, *args, **options):
        # Filter onganizations with an active reminder mail
        organizations = Organization.objects.filter(mailtemplate__name='reminder', mailtemplate__is_active=True)

        for organization in organizations:
            memberships = organization.membership_set.filter(is_tender=True, is_active=True)

            now = timezone.now()
            events = organization.participates.filter(starts_at__gte=now, is_closed=False).order_by('starts_at', )

            # Load template and settings
            try:
                mailtemplate = MailTemplate.objects.get(organization=organization, name="reminder", is_active=True)
                starts_before = now + timedelta(minutes=mailtemplate.send_at) if mailtemplate.send_at else None
            except MailTemplate.DoesNotExist:
                raise CommandError('MailTemplate "reminder" does not exist for %s' % organization)

            for membership in memberships:
                user = membership.user
                if not user.email:
                    self.stderr.write('%s heeft geen e-mailadres.\n' % (user,))
                    continue

                missing_events = events.exclude(pk__in=user.event_set.values_list('id', flat=True))
                if starts_before is not None:
                    missing_events = missing_events.exclude(starts_at__gte=starts_before)
                addressees = [user]

                if len(missing_events) > 0:
                    mail(settings.EMAIL_FROM, addressees, mailtemplate.subject, mailtemplate.template,
                         extraattrs={'missing_events': missing_events, 'now': now})
