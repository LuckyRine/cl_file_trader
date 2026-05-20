from django.contrib import admin
from django.utils.html import format_html
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price_monthly", "limit_type", "upload_limit",
                    "max_file_size_display", "storage_quota_display", "is_active"]
    list_editable = ["is_active"]
    list_filter = ["limit_type", "is_active"]

    @admin.display(description="Max file size")
    def max_file_size_display(self, obj):
        return f"{obj.max_file_size // 1024 // 1024} MB"

    @admin.display(description="Storage quota")
    def storage_quota_display(self, obj):
        gb = obj.storage_quota / 1024 / 1024 / 1024
        return f"{gb:.1f} GB"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status_badge", "current_period_end",
                    "stripe_sub_id", "created_at"]
    list_filter = ["status", "plan"]
    search_fields = ["user__email", "stripe_sub_id"]
    raw_id_fields = ["user"]
    readonly_fields = ["created_at"]

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {"active": "#198754", "cancelled": "#6c757d", "past_due": "#dc3545"}
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )

    actions = ["cancel_subscriptions"]

    @admin.action(description="Cancel selected subscriptions")
    def cancel_subscriptions(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} subscription(s) cancelled.")