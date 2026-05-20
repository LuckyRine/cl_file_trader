from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AdBanner
from .tasks import record_ad_click, record_ad_impression

class AdServeView(APIView):
    def get(self, request, placement):
        from django.utils import timezone
        now = timezone.now()
        banner = AdBanner.objects.filter(
            placement=placement, is_active=True,
            starts_at__lte=now, ends_at__gte=now
        ).order_by("?").first()   # random; swap for CPM/CPC priority

        if not banner:
            return Response({"ad": None})

        record_ad_impression.delay(banner.id,
                                   getattr(request.user, "id", None),
                                   request.META.get("REMOTE_ADDR"))
        return render(request, "ads/banner.html", {"banner": banner})

class AdClickView(APIView):
    def get(self, request, banner_id):
        from django.shortcuts import redirect
        record_ad_click.delay(banner_id)
        banner = AdBanner.objects.get(id=banner_id)
        return redirect(banner.target_url)