from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-created_at"]
    list_display = ["email", "username", "plan_badge", "storage_used_display",
                    "is_active", "is_staff", "created_at"]
    list_filter = ["is_active", "is_staff", "subscription__plan"]
    search_fields = ["email", "username"]
    readonly_fields = ["id", "created_at", "storage_used_display", "uploads_this_month"]

    fieldsets = (
        ("Identity", {"fields": ("id", "email", "username", "avatar", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups")}),
        ("Stats",       {"fields": ("storage_used_display", "uploads_this_month", "created_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )

    @admin.display(description="Plan")
    def plan_badge(self, obj):
        sub = getattr(obj, "subscription", None)
        name = sub.plan.name if sub else "Free"
        colors = {"Free": "#6c757d", "Pro": "#0d6efd", "Business": "#198754"}
        color = colors.get(name, "#6c757d")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            color, name
        )

    @admin.display(description="Storage used")
    def storage_used_display(self, obj):
        mb = obj.get_storage_used() / 1024 / 1024
        return f"{mb:.1f} MB"

    @admin.display(description="Uploads this month")
    def uploads_this_month(self, obj):
        return obj.get_upload_count_this_month()