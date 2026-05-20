from django.shortcuts import render
from django.views import View
from apps.files.models import File
from django.db.models import Q


class FileSearchView(View):
    """
    GET /search/?q=report&mime=pdf&page=1
    Works without Elasticsearch — falls back to DB icontains search.
    When ES is enabled, swap the queryset logic for FileDocument.search().
    """
    template_name = "search/search.html"

    def get(self, request):
        query = request.GET.get("q", "").strip()
        mime  = request.GET.get("mime", "").strip()
        page  = int(request.GET.get("page", 1))
        size  = 20

        files = File.objects.filter(is_public=True, status="ready") \
                            .select_related("owner")

        if query:
            files = files.filter(
                Q(original_name__icontains=query) |
                Q(owner__username__icontains=query)
            )

        if mime:
            files = files.filter(mime_type__icontains=mime)

        files = files.order_by("-created_at")

        # simple manual pagination
        total      = files.count()
        offset     = (page - 1) * size
        results    = files[offset: offset + size]
        total_pages = (total + size - 1) // size

        # distinct mime types for filter dropdown
        mime_types = File.objects.filter(
            is_public=True, status="ready"
        ).values_list("mime_type", flat=True).distinct()

        return render(request, self.template_name, {
            "results":     results,
            "query":       query,
            "mime":        mime,
            "total":       total,
            "page":        page,
            "total_pages": total_pages,
            "mime_types":  mime_types,
            "has_prev":    page > 1,
            "has_next":    page < total_pages,
        })


# ── API view (for ES when ready) ─────────────────────────────────────────────
from rest_framework.views import APIView
from rest_framework.response import Response


class FileSearchAPIView(APIView):
    """GET /api/search/?q=...  — JSON, ready to swap to ES"""

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        mime  = request.query_params.get("mime", "")
        page  = int(request.query_params.get("page", 1))
        size  = 20

        files = File.objects.filter(is_public=True, status="ready") \
                            .select_related("owner")
        if query:
            files = files.filter(
                Q(original_name__icontains=query) |
                Q(owner__username__icontains=query)
            )
        if mime:
            files = files.filter(mime_type__icontains=mime)

        total   = files.count()
        offset  = (page - 1) * size
        results = files[offset: offset + size]

        return Response({
            "total":   total,
            "page":    page,
            "results": [{
                "id":    str(f.id),
                "name":  f.original_name,
                "mime":  f.mime_type,
                "owner": f.owner.username,
                "slug":  f.slug,
                "size":  f.size,
            } for f in results],
        })