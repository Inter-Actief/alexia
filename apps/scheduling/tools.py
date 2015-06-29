from django.conf import settings

from utils.mail import mail


def notify_tenders(sender, instance, **kwargs):
    from apps.scheduling.models import Event, MailTemplate

    send_mail = False

    if instance.pk is not None:
        orig = Event.objects.get(pk=instance.pk)
        if orig.is_closed != instance.is_closed and not instance.is_closed:
            send_mail = True
    else:
        send_mail = not instance.is_closed

    if send_mail:
        try:
            mt = MailTemplate.objects.get(organization=instance.organizer,
                                          name="enrollopen")
            if mt.is_active:
                addressees = [m.user for m in instance.organizer.membership_set.filter(is_tender=True)]
                mail(settings.EMAIL_FROM, addressees, mt.subject, mt.template,
                     extraattrs={'event': instance})
        except MailTemplate.DoesNotExist:
            pass
