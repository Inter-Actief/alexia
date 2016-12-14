from django.conf import settings

from alexia.utils.mail import mail


def notify_tenders(sender, instance, **kwargs):
    from alexia.apps.scheduling.models import Event, MailTemplate

    mail_template = None

    if instance.pk is None:
        if not instance.is_closed:
            mail_template = "enrollopen"
    else:
        orig = Event.objects.get(pk=instance.pk)
        if orig.is_closed and not instance.is_closed:
            mail_template = "enrollopen"
        elif not orig.is_closed and instance.is_closed:
            mail_template = "enrollclosed"

    if mail_template:
        try:
            mt = MailTemplate.objects.get(organization=instance.organizer, name=mail_template)
            if mt.is_active:
                members = instance.organizer.membership_set.filter(is_tender=True, is_active=True) \
                    .exclude(user__email="")
                addressees = [m.user for m in members]
                mail(settings.EMAIL_FROM, addressees, mt.subject, mt.template, extraattrs={'event': instance})
        except MailTemplate.DoesNotExist:
            pass
