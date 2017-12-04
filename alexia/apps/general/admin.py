from django.contrib import admin

from .models import Auditlog


@admin.register(Auditlog)
class AuditlogAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    list_filter = ["action", "timestamp"]
    list_display = ["timestamp", "user", "action", "extra"]
    search_fields = ["user__username", "user__email", "extra"]
