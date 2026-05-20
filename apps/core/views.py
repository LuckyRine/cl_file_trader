# apps/core/views.py
from django.shortcuts import render
from django.views import View


class HomeView(View):
    template_name = "home.html"

    def get(self, request):
        from apps.files.models import File
        from apps.accounts.models import User

        recent_files = File.objects.filter(
            is_public=True, status="ready"
        ).select_related("owner")[:6]

        stats = {
            "total_files":     File.objects.filter(status="ready").count(),
            "total_downloads": sum(File.objects.values_list("downloads", flat=True)),
            "total_users":     User.objects.filter(is_active=True).count(),
        }

        return render(request, self.template_name, {
            "recent_files": recent_files,
            "stats":        stats,
        })