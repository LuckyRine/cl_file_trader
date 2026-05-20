from django.contrib import admin
from django.utils.html import format_html
from django.utils.timesince import timesince
from .models import File


class FileStatusFilter(admin.SimpleListFilter):
    title = "Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [("ready", "Ready"), ("processing", "Processing"), ("failed", "Failed")]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ["original_name", "owner", "size_display", "mime_type",
                    "status_badge", "downloads", "is_public", "expires_at", "created_at"]
    list_filter = [FileStatusFilter, "is_public", "mime_type"]
    search_fields = ["original_name", "owner__email", "slug"]
    readonly_fields = ["id", "slug", "size", "mime_type", "downloads", "created_at"]
    raw_id_fields = ["owner"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("File", {"fields": ("id", "original_name", "file", "mime_type", "size", "slug")}),
        ("Access", {"fields": ("owner", "is_public", "password", "expires_at")}),
        ("State", {"fields": ("status", "downloads", "created_at")}),
    )

    @admin.display(description="Size")
    def size_display(self, obj):
        kb = obj.size / 1024
        return f"{kb:.1f} KB" if kb < 1024 else f"{kb/1024:.1f} MB"

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {"ready": "#198754", "processing": "#ffc107", "failed": "#dc3545"}
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )

    actions = ["mark_ready", "mark_failed", "delete_files_and_records"]

    @admin.action(description="Mark selected as Ready")
    def mark_ready(self, request, queryset):
        queryset.update(status="ready")

    @admin.action(description="Mark selected as Failed")
    def mark_failed(self, request, queryset):
        queryset.update(status="failed")

    @admin.action(description="Delete files + DB records")
    def delete_files_and_records(self, request, queryset):
        for f in queryset:
            f.file.delete(save=False)
            f.delete()
        self.message_user(request, "Files and records deleted.")