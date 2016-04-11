from __future__ import absolute_import

# Load default settings
from .default import *  # noqa

# Load local settings
try:
    from .local import *  # noqa
except ImportError:
    pass

# Debug toolbar
if DEBUG:
    # Enable debug toolbar if DEBUG is enabled.

    def show_toolbar(request):
        return True

    INSTALLED_APPS += ('debug_toolbar',)
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': 'settings.show_toolbar'
    }
