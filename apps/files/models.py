import uuid, os
from django.db import models
from django.conf import settings

def upload_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"files/{instance.owner.id}/{uuid.uuid4()}.{ext}"

class File(models.Model):
    STATUS = [("processing","Processing"),("ready","Ready"),("failed","Failed")]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner       = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE, related_name="files")
    original_name = models.CharField(max_length=255)
    file        = models.FileField(upload_to=upload_path)
    size        = models.BigIntegerField(default=0)
    mime_type   = models.CharField(max_length=100, default="application/octet-stream")
    slug        = models.SlugField(unique=True, max_length=12)   # short link
    status      = models.CharField(max_length=20, choices=STATUS, default="processing")
    is_public   = models.BooleanField(default=True)
    password    = models.CharField(max_length=128, blank=True)   # optional protection
    downloads   = models.PositiveIntegerField(default=0)
    expires_at  = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return self.original_name

    def save(self, *args, **kwargs):
        if self.file:
            self.size = self.file.size

        super().save(*args, **kwargs)

    def is_expired(self):
        from django.utils import timezone
        return self.expires_at and timezone.now() > self.expires_at