from django.core.mail import send_mass_mail
from django.template import Context, Template


def mail(fromaddr, addressees, subject, mailbody, replyto=None, extraattrs=None):
    """
    Mail to people.
    The following extraattrs are needed for correct mailing.
    For the reservation mail: event.
    For the enroll mail: event.
    For the reminder mail: event.
    For the fustdiff mail: event.
    """
    if extraattrs is None:
        extraattrs = {}

    def _generate_mail():
        for addressee in addressees:
            if not addressee.email:
                continue

            attrs = {'addressee': addressee}
            attrs.update(extraattrs)
            subjecttext = Template(subject).render(Context(attrs))
            text = Template(mailbody).render(Context(attrs))
            to = ['"%s" <%s>' % (addressee.get_full_name(), addressee.email), ]
            yield (subjecttext, text, fromaddr, to)

    send_mass_mail(_generate_mail(), fail_silently=False)
