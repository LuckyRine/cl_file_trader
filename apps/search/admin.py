from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.contrib import messages


class SearchIndexAdmin(admin.ModelAdmin):
    """
    Mixin — add to any ModelAdmin to expose
    a one-click 'Rebuild ES index' button in the changelist.
    """
    change_list_template = "admin/search/reindex_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("reindex/",
                 self.admin_site.admin_view(self.reindex_view),
                 name="search_reindex"),
        ]
        return custom + urls

    def reindex_view(self, request):
        from apps.search.documents import FileDocument
        from apps.files.models import File
        try:
            FileDocument().update(File.objects.filter(status="ready"))
            self.message_user(request, "Elasticsearch index rebuilt successfully.",
                              messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Re-index failed: {e}", messages.ERROR)
        return HttpResponseRedirect("../")


# Lightweight proxy — lets you trigger ES reindex from Django admin
# without exposing the File model twice.
from apps.files.models import File as FileModel

class FileSearchProxy(FileModel):
    class Meta:
        proxy = True
        verbose_name = "Search Index"
        verbose_name_plural = "Search Index (Elasticsearch)"
        app_label = "search"


@admin.register(FileSearchProxy)
class FileSearchProxyAdmin(SearchIndexAdmin):
    list_display = ["original_name", "owner", "mime_type", "status", "created_at"]
    search_fields = ["original_name", "owner__email"]
    list_filter = ["status", "mime_type"]
    readonly_fields = [f.name for f in FileModel._meta.fields]

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False