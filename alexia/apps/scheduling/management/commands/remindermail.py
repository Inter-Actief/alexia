from django.core.management.base import BaseCommand
from django.utils import timezone

from alexia.apps.scheduling.models import MailTemplate
from alexia.core.mail import template_mass_mail


class Command(BaseCommand):
    help = 'Send reminder mails for events with missing availabilities'

    def handle(self, *args, **options):
        for mailtemplate in MailTemplate.objects.filter(name=MailTemplate.REMINDER, is_active=True):
            now = timezone.now()
            organization = mailtemplate.organization
            if organization.is_active:
                bartenders = organization.membership_set.filter(is_tender=True, is_active=True, user__email__isnull=False)
                events = organization.participates.filter(starts_at__gte=now, is_closed=False).order_by('starts_at')

                recipients = []
                for bartender in bartenders:
                    missing_events = events.exclude(pk__in=bartender.user.event_set.values_list('id', flat=True))
                    context = {'addressee': bartender.user, 'missing_events': missing_events, 'now': now}
                    recipients.append(([bartender.user.email], context))
                template_mass_mail(mailtemplate.subject, mailtemplate.template, recipients)
