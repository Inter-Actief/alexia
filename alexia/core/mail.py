from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import Context, Template
from django.utils.html import strip_tags


def template_mass_mail(subject, message, recipient_context_list=None):
    connection = get_connection()

    subject = Template(subject)
    html_message = Template(message)
    message = Template(strip_tags(message))

    messages = []
    for recipient_list, context in recipient_context_list:
        context = Context(context)
        mail = EmailMultiAlternatives(
            subject.render(context),
            message.render(context),
            to=recipient_list,
            connection=connection,
        )
        mail.attach_alternative(html_message.render(context), 'text/html')
        messages.append(mail)

    connection.send_messages(messages)
