from django import forms


class NativeSplitDateTimeWidget(forms.SplitDateTimeWidget):
    """SplitDateTimeWidget using the browser's native date and time inputs."""

    def __init__(self, attrs=None):
        super(NativeSplitDateTimeWidget, self).__init__(
            attrs=attrs,
            date_attrs={'type': 'date'},
            time_attrs={'type': 'time'},
            date_format='%Y-%m-%d',
            time_format='%H:%M',
        )
