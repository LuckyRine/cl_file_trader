from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class CanUploadPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        sub = getattr(user, "subscription", None)
        if sub is None:
            # free tier: check default limits
            from apps.subscriptions.models import Plan
            free = Plan.objects.filter(name="Free").first()
            if free and user.get_upload_count_this_month() >= free.upload_limit:
                raise PermissionDenied("Free plan limit reached. Please upgrade.")
            return True
        file = request.FILES.get("file")
        size = file.size if file else 0
        if not sub.can_upload(user):
            raise PermissionDenied("Monthly upload limit reached.")
        if file and size > sub.plan.max_file_size:
            raise PermissionDenied(f"File exceeds plan limit of {sub.plan.max_file_size} bytes.")
        if file and not sub.has_storage(user, size):
            raise PermissionDenied("Storage quota exceeded.")
        return True