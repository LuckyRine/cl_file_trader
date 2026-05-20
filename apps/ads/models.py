from django.db import models

class AdBanner(models.Model):
    PLACEMENT = [("home_top","Home Top"),("download_sidebar","Download Sidebar"),
                 ("upload_bottom","Upload Bottom")]

    title      = models.CharField(max_length=100)
    image      = models.ImageField(upload_to="ads/")
    target_url = models.URLField()
    placement  = models.CharField(max_length=30, choices=PLACEMENT)
    impressions = models.PositiveBigIntegerField(default=0)
    clicks     = models.PositiveBigIntegerField(default=0)
    is_active  = models.BooleanField(default=True)
    starts_at  = models.DateTimeField()
    ends_at    = models.DateTimeField()

    def ctr(self):
        return round(self.clicks / self.impressions * 100, 2) if self.impressions else 0

    def is_running(self):
        from django.utils import timezone

        if not self.starts_at or not self.ends_at:
            return False
        now = timezone.now()
        return self.is_active and self.starts_at <= now <= self.ends_at


class AdImpression(models.Model):
    banner     = models.ForeignKey(AdBanner, on_delete=models.CASCADE)
    user       = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)