from django.urls import path
from . import views as subv

urlpatterns = [
    # HTML pages
    path("pricing/", subv.PricingView.as_view(), name="pricing"),
    path("pricing/checkout/<int:plan_id>/", subv.CheckoutView.as_view(), name="checkout"),
    # API
    path("api/subs/plans/", subv.PlanListAPIView.as_view(), name="api_plans"),
    path("api/subs/webhook/", subv.StripeWebhookView.as_view(), name="stripe_webhook"),
]
