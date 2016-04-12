from django.db import models


class PublicOrganizationManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(PublicOrganizationManager, self).get_queryset().exclude(is_public=False)
