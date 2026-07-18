from django import forms


class NativeSplitDateTimeWidget(forms.SplitDateTimeWidget):
    """SplitDateTimeWidget using the browser's native date and time inputs, rendered inline and compact."""

    def __init__(self, attrs=None):
        super(NativeSplitDateTimeWidget, self).__init__(
            attrs=attrs,
            date_attrs={'type': 'date', 'class': 'd-inline-block me-2', 'style': 'width: 10rem'},
            time_attrs={'type': 'time', 'class': 'd-inline-block', 'style': 'width: 7rem'},
            date_format='%Y-%m-%d',
            time_format='%H:%M',
        )
