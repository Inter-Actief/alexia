from alexia.conf.settings.base import *

# Try to import local settings, fallback to config via environment variables if that fails
try:
	from alexia.conf.settings.local import *
except ImportError:
	from alexia.conf.settings.environ import *
