from celery import shared_task


@shared_task
def record_ad_impression(banner_id: int, user_id, ip_address: str):
    from .models import AdBanner, AdImpression
    from apps.accounts.models import User

    banner = AdBanner.objects.get(id=banner_id)
    AdBanner.objects.filter(id=banner_id).update(impressions=banner.impressions + 1)

    AdImpression.objects.create(
        banner     = banner,
        user_id    = user_id,
        ip_address = ip_address or "0.0.0.0",
    )


@shared_task
def record_ad_click(banner_id: int):
    from .models import AdBanner
    AdBanner.objects.filter(id=banner_id).update(
        clicks=AdBanner.objects.get(id=banner_id).clicks + 1
    )