from django.db import models


class ActiveOrganizationManager(models.Manager):
    def filter_active(self, request):
        """
        Filters active organizations unless superuser or foundation manager
        """

        only_active = not (hasattr(request, 'user') and (request.user.is_superuser or request.user.profile.is_foundation_manager))

        if only_active:
            return self.filter(is_active=True)
        else:
            return self.all()