from django.db import models


class PermanentProductManager(models.Manager):
    """Provides several extra handy methods to find events."""
    def get_queryset(self):
        return super(PermanentProductManager, self).get_queryset().filter(deleted=False)


class TemporaryProductManager(models.Manager):
    """Provides several extra handy methods to find events."""
    def get_queryset(self):
        return super(TemporaryProductManager, self).get_queryset().filter(deleted=False)
