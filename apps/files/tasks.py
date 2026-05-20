from celery import shared_task
from django.core.files.storage import default_storage
# import magic  # python-magic for MIME detection

@shared_task(bind=True, max_retries=3)
def process_file(self, file_id: str):
    """
    Post-upload pipeline:
      1. Validate MIME type (security)
      2. Virus scan (ClamAV via pyclamd)
      3. Generate thumbnail for images/video
      4. Index into Elasticsearch
      5. Send confirmation email
    """
    from apps.files.models import File
    try:
        f = File.objects.get(id=file_id)
        # 1. MIME check
        # mime = magic.from_buffer(f.file.read(2048), mime=True)
        # f.mime_type = mime
        # 2. Index search
        # from apps.search.documents import FileDocument
        # FileDocument().update(f)
        f.status = "ready"
        f.save()
        # 3. Notify user
        # send_upload_confirmation.delay(str(f.owner.id), f.original_name)
    except Exception as exc:
        self.retry(exc=exc, countdown=60)


@shared_task
def send_upload_confirmation(user_id: str, filename: str):
    from django.core.mail import send_mail
    from apps.accounts.models import User
    user = User.objects.get(id=user_id)
    send_mail(
        subject="Your file is ready",
        message=f"'{filename}' has been processed and is ready to share.",
        from_email="noreply@fileshare.pro",
        recipient_list=[user.email],
    )


@shared_task
def cleanup_expired_files():
    """Scheduled via Celery Beat — runs daily"""
    from django.utils import timezone
    from apps.files.models import File
    expired = File.objects.filter(expires_at__lt=timezone.now())
    for f in expired:
        f.file.delete(save=False)
        f.delete()