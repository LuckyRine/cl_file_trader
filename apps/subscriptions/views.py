from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Plan, Subscription


class PricingView(View):
    """GET /pricing/ — public pricing page"""
    template_name = "subscriptions/pricing.html"

    def get(self, request):
        plans = Plan.objects.filter(is_active=True).order_by("price_monthly")
        current_plan = None
        if request.user.is_authenticated:
            sub = getattr(request.user, "subscription", None)
            current_plan = sub.plan.name if sub else "Free"

        return render(request, self.template_name, {
            "plans":        plans,
            "current_plan": current_plan,
        })


@method_decorator(login_required, name="dispatch")
class CheckoutView(View):
    """GET /pricing/checkout/<plan_id>/ — start Stripe checkout"""
    template_name = "subscriptions/checkout.html"

    def get(self, request, plan_id):
        plan = Plan.objects.filter(id=plan_id, is_active=True).first()
        if not plan:
            messages.error(request, "Plan not found.")
            return redirect("pricing")

        return render(request, self.template_name, {"plan": plan})

    def post(self, request, plan_id):
        # Stripe integration point — wire in when ready
        messages.info(request, "Stripe checkout coming soon.")
        return redirect("pricing")


# ── API ───────────────────────────────────────────────────────────────────────

class PlanListAPIView(APIView):
    """GET /api/subs/plans/"""

    def get(self, request):
        plans = Plan.objects.filter(is_active=True).order_by("price_monthly")
        return Response([{
            "id":             p.id,
            "name":           p.name,
            "price_monthly":  str(p.price_monthly),
            "limit_type":     p.limit_type,
            "upload_limit":   p.upload_limit,
            "max_file_size":  p.max_file_size,
            "storage_quota":  p.storage_quota,
        } for p in plans])


class StripeWebhookView(APIView):
    """POST /api/subs/webhook/ — Stripe webhook handler"""

    def post(self, request):
        # Wire in stripe.Webhook.construct_event() here
        return Response({"status": "ok"})