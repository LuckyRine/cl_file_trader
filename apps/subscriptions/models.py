from django.db import models
from django.conf import settings

class Plan(models.Model):
    LIMIT_TYPE = [
        ("count",     "Upload Count"),
        ("unlimited", "Unlimited"),
    ]
    name          = models.CharField(max_length=50)          # Free / Pro / Business
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    limit_type    = models.CharField(max_length=20, choices=LIMIT_TYPE, default="count")
    upload_limit  = models.IntegerField(default=5)           # ignored if unlimited
    max_file_size = models.BigIntegerField(default=50 * 1024 * 1024)  # bytes
    storage_quota = models.BigIntegerField(default=500 * 1024 * 1024) # bytes
    stripe_price_id = models.CharField(max_length=100, blank=True)
    is_active     = models.BooleanField(default=True)

    def __str__(self): return self.name


class Subscription(models.Model):
    STATUS = [("active","Active"),("cancelled","Cancelled"),("past_due","Past Due")]

    user           = models.OneToOneField(settings.AUTH_USER_MODEL,
                                          on_delete=models.CASCADE,
                                          related_name="subscription")
    plan           = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status         = models.CharField(max_length=20, choices=STATUS, default="active")
    stripe_sub_id  = models.CharField(max_length=100, blank=True)
    current_period_end = models.DateTimeField(null=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        return self.status == "active"

    def can_upload(self, user):
        if self.plan.limit_type == "unlimited":
            return True
        return user.get_upload_count_this_month() < self.plan.upload_limit

    def has_storage(self, user, file_size):
        return (user.get_storage_used() + file_size) <= self.plan.storage_quota