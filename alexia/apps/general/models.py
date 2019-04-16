import jsonfield
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class Auditlog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        null=True,
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    action = models.CharField(max_length=50, db_index=True)
    content_type = models.ForeignKey(ContentType, models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField(null=True)
    obj = GenericForeignKey("content_type", "object_id")
    extra = jsonfield.JSONField()

    class Meta:
        ordering = ["-timestamp"]


def log(user, action, extra=None, obj=None, dateof=None):
    if (user is not None and not user.is_authenticated()):
        user = None

    if extra is None:
        extra = {}

    content_type = None
    object_id = None

    if obj is not None:
        content_type = ContentType.objects.get_for_model(obj)
        object_id = obj.pk

    if dateof is None:
        dateof = timezone.now()

    Auditlog.objects.create(
        user=user,
        action=action,
        extra=extra,
        content_type=content_type,
        object_id=object_id,
        timestamp=dateof
    )
