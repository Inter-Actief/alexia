from alexia.core.mail import template_mass_mail


def notify_tenders(sender, instance, **kwargs):
    from .models import Event, MailTemplate
    mail_template = None

    if not instance.pk:
        if not instance.is_closed:
            mail_template = MailTemplate.ENROLL_OPEN
    else:
        orig = Event.objects.get(pk=instance.pk)
        if orig.is_closed and not instance.is_closed:
            mail_template = MailTemplate.ENROLL_OPEN
        elif not orig.is_closed and instance.is_closed:
            mail_template = MailTemplate.ENROLL_CLOSED

    if mail_template:
        try:
            mt = MailTemplate.objects.get(organization=instance.organizer, name=mail_template, is_active=True)
            bartenders = instance.organizer.membership_set.filter(is_tender=True, is_active=True) \
                                                          .exclude(user__email='')
            recipients = [
                ([bartender.user.email], {'addressee': bartender.user, 'event': instance})
                for bartender in bartenders.exclude(user__email='')
            ]
            template_mass_mail(mt.subject, mt.template, recipients)
        except MailTemplate.DoesNotExist:
            pass
