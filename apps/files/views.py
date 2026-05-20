# apps/files/views.py
import uuid

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.http import FileResponse, Http404
import mimetypes

from rest_framework import generics, permissions, parsers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import File
from apps.subscriptions.permissions import CanUploadPermission


# ── API Views ─────────────────────────────────────────────────────────────────

class FileUploadAPIView(APIView):
    """POST /api/files/upload/ — used by HTMX form"""
    permission_classes = [permissions.IsAuthenticated, CanUploadPermission]
    parser_classes     = [parsers.MultiPartParser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided."}, status=400)

        # optional fields
        password   = request.POST.get("password", "")
        expires_in = request.POST.get("expires_in", "")  # days as string

        expires_at = None
        if expires_in:
            try:
                expires_at = timezone.now() + timezone.timedelta(days=int(expires_in))
            except ValueError:
                pass

        f = File(
            owner         = request.user,
            original_name = file.name,
            file          = file,
            size          = file.size,
            mime_type     = file.content_type or "application/octet-stream",
            slug          = uuid.uuid4().hex[:12],
            expires_at    = expires_at,
            status        = "ready",
        )
        if password:
            f.set_password(password)

        f.save()

        # from .tasks import process_file
        # process_file.delay(str(f.id))


        return Response({
            "id":            str(f.id),
            "original_name": f.original_name,
            "slug":          f.slug,
            "size":          f.size,
            "status":        f.status,
            "share_url":     request.build_absolute_uri(f"/f/{f.slug}/"),
        }, status=201)


class FileDownloadAPIView(APIView):
    """GET /api/files/<slug>/ — returns download URL"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        f = get_object_or_404(File, slug=slug, status="ready")

        if f.is_expired():
            return Response({"detail": "Link expired."}, status=410)

        if f.password:
            pwd = request.query_params.get("password", "")
            if not f.check_password(pwd):
                return Response({"detail": "Password required."}, status=403)

        # File.objects.filter(pk=f.pk).update(downloads=f.downloads + 1)
        #
        # response = FileResponse(f.file.open("rb"))
        #
        # response["Content-Disposition"] = f'attachment; filename="{f.original_name}"'
        #
        # return response

        File.objects.filter(pk=f.pk).update(downloads=f.downloads + 1)
        return Response({"url": f.file.url, "name": f.original_name})


class UserFileListAPIView(generics.ListAPIView):
    """GET /api/files/my/ — JSON list of user's files"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return File.objects.filter(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        data = [{
            "id":            str(f.id),
            "original_name": f.original_name,
            "slug":          f.slug,
            "size":          f.size,
            "mime_type":     f.mime_type,
            "downloads":     f.downloads,
            "status":        f.status,
            "is_public":     f.is_public,
            "expires_at":    f.expires_at.isoformat() if f.expires_at else None,
            "created_at":    f.created_at.isoformat(),
        } for f in self.get_queryset()]
        return Response(data)


class FileDeleteAPIView(APIView):
    """DELETE /api/files/<slug>/delete/"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, slug):
        f = get_object_or_404(File, slug=slug, owner=request.user)
        f.file.delete(save=False)
        f.delete()
        return Response({"detail": "Deleted."}, status=204)

class FileServeView(APIView):
    """GET /api/files/<slug>/serve/ — отдаёт файл с оригинальным именем"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        f = get_object_or_404(File, slug=slug, status="ready")

        if f.is_expired():
            raise Http404

        try:
            response = FileResponse(
                f.file.open("rb"),
                content_type=f.mime_type or "application/octet-stream",
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{f.original_name}"'
            )
            response["Content-Length"] = f.size
            return response
        except Exception:
            raise Http404

# ── Template Views (HTML pages) ───────────────────────────────────────────────


@method_decorator(login_required, name="dispatch")
class UploadPageView(View):
    """GET /upload/ — upload page with drag & drop"""
    template_name = "upload.html"

    def get(self, request):
        sub          = getattr(request.user, "subscription", None)
        uploads_used = request.user.get_upload_count_this_month()

        if sub:
            if sub.plan.limit_type == "unlimited":
                uploads_left = "∞"
            else:
                uploads_left = max(0, sub.plan.upload_limit - uploads_used)
        else:
            # free plan default
            from apps.subscriptions.models import Plan
            free = Plan.objects.filter(name="Free").first()
            limit = free.upload_limit if free else 5
            uploads_left = max(0, limit - uploads_used)

        return render(request, self.template_name, {
            "uploads_left": uploads_left,
            "storage_used": request.user.get_storage_used(),
        })


class DownloadPageView(View):
    """GET /f/<slug>/ — public download page"""
    template_name = "download.html"

    def get(self, request, slug):
        try:
            f = File.objects.select_related("owner").get(slug=slug)
        except File.DoesNotExist:
            return render(request, "download.html", {"file_not_found": True})

        if f.is_expired():
            return render(request, "download.html", {"file_expired": True})

        return render(request, self.template_name, {"file": f})


@method_decorator(login_required, name="dispatch")
class MyFilesView(View):
    """GET /my-files/ — dashboard with user's files"""
    template_name = "files/my_files.html"

    def get(self, request):
        files = File.objects.filter(
            owner=request.user
        ).order_by("-created_at")

        return render(request, self.template_name, {
            "files":         files,
            "storage_used":  request.user.get_storage_used(),
            "uploads_month": request.user.get_upload_count_this_month(),
        })