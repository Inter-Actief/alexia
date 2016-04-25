import icalendar
from django import http


def generate_ical(events, name='Alexia', tender=False):
    cal = icalendar.Calendar()

    cal.add('prodid', '-//inter-actief//alexia//NL')
    cal.add('calscale', 'GREGORIAN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', name)

    for event in events:
        e = icalendar.Event()

        e.add('dtstamp', event.starts_at)
        e.add('dtstart', event.starts_at)
        e.add('dtend', event.ends_at)
        e.add('location', event.location.all()[0].name)
        e.add('uid', event.pk)

        if event.option:
            e.add('status', 'TENTATIVE')
        else:
            e.add('status', 'CONFIRMED')

        if tender:
            e.add('summary', '[Tappen] %s' % event.name)
            e.add('transp', 'OPAQUE')
        else:
            e.add('summary', event.name)
            e.add('transp', 'TRANSPARENT')

        description = event.tender_comments if tender else event.description
        if description:
            e.add('description', description)

        for ba in event.get_assigned_bartenders():
            bartender = icalendar.vCalAddress('MAILTO:noreply@alex.ia.utwente.nl')
            bartender.params['cn'] = icalendar.vText(ba.get_full_name())
            bartender.params['partstat'] = icalendar.vText('ACCEPTED')
            e.add('attendee', bartender, encode=0)

        cal.add_component(e)

    return cal.to_ical()


class IcalResponse(http.HttpResponse):
    def __init__(self, content=b'', *args, **kwargs):
        kwargs['content_type'] = 'text/calendar; charset=utf-8'
        super(IcalResponse, self).__init__(content, *args, **kwargs)
