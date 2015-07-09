#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, "/data/applications/wwwers/packages/Django-1.7.9")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
