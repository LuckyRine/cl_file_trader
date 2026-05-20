from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.utils.html import mark_safe

from .models import AdBanner, AdImpression


class RunningFilter(admin.SimpleListFilter):
    title = "Running now"
    parameter_name = "running"

    def lookups(self, request, model_admin):
        return [("yes", "Live"), ("no", "Not live")]

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "yes":
            return queryset.filter(
                is_active=True,
                starts_at__lte=now,
                ends_at__gte=now,
            )
        if self.value() == "no":
            return queryset.exclude(
                is_active=True,
                starts_at__lte=now,
                ends_at__gte=now,
            )
        return queryset

@admin.register(AdBanner)
class AdBannerAdmin(admin.ModelAdmin):
    list_display  = [
        "title", "placement", "get_live_badge", "impressions",
        "clicks", "get_ctr", "starts_at", "ends_at", "is_active",
    ]
    list_filter   = [RunningFilter, "placement", "is_active"]
    search_fields = ["title"]
    # list_editable = ["is_active"]  ← убираем это
    readonly_fields = ["impressions", "clicks", "get_ctr", "get_preview"]

    fieldsets = (
        ("Creative", {"fields": ("title", "image", "get_preview", "target_url")}),
        ("Targeting", {"fields": ("placement", "is_active", "starts_at", "ends_at")}),
        ("Stats",     {"fields": ("impressions", "clicks", "get_ctr")}),
    )

    def get_ctr(self, obj):
        return f"{obj.ctr()}%"
    get_ctr.short_description = "CTR"

    def get_live_badge(self, obj):
        try:
            if obj.is_running():
                return mark_safe('<span style="color:#198754;font-weight:700">● Live</span>')
        except Exception:
            pass
        return mark_safe('<span style="color:#6c757d">○ Paused</span>')

    get_live_badge.short_description = "Live"

    def get_preview(self, obj):
        if obj.image:
            try:
                return mark_safe(f'<img src="{obj.image.url}" style="max-height:80px;border-radius:6px">')
            except Exception:
                return "—"
        return "—"

    get_preview.short_description = "Preview"


@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):
    list_display    = ["banner", "user", "ip_address", "created_at"]
    list_filter     = ["banner"]
    search_fields   = ["ip_address", "user__email"]
    readonly_fields = ["banner", "user", "ip_address", "created_at"]
    date_hierarchy  = "created_at"

    def has_add_permission(self, request):              return False
    def has_change_permission(self, request, obj=None): return False