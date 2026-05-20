# apps/accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator

from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserProfileSerializer
from .models import User


# ── API Views ─────────────────────────────────────────────────────────────────

class RegisterAPIView(generics.CreateAPIView):
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class   = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── Template Views ────────────────────────────────────────────────────────────

class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request):
        email     = request.POST.get("email", "").strip()
        username  = request.POST.get("username", "").strip()
        password  = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        errors = {}
        if not email:
            errors["email"] = "Email is required."
        elif User.objects.filter(email=email).exists():
            errors["email"] = "This email is already registered."

        if not username:
            errors["username"] = "Username is required."
        elif User.objects.filter(username=username).exists():
            errors["username"] = "This username is already taken."

        if len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."
        elif password != password2:
            errors["password2"] = "Passwords do not match."

        if errors:
            return render(request, self.template_name, {
                "errors":   errors,
                "email":    email,
                "username": username,
            })

        user = User.objects.create_user(
            email=email, username=username, password=password,
        )
        login(request, user)
        messages.success(request, f"Welcome, {user.username}!")
        return redirect("home")


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name, {
            "next": request.GET.get("next", ""),
        })

    def post(self, request):
        email    = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        next_url = request.POST.get("next", "")

        user = authenticate(request, username=email, password=password)

        if user is None:
            return render(request, self.template_name, {
                "error": "Invalid email or password.",
                "email": email,
                "next":  next_url,
            })

        if not user.is_active:
            return render(request, self.template_name, {
                "error": "This account has been deactivated.",
                "email": email,
            })

        login(request, user)
        return redirect(next_url if next_url else "home")


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "You have been signed out.")
        return redirect("home")


@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    template_name = "accounts/profile.html"

    def get(self, request):
        user         = request.user
        storage_used = user.get_storage_used()
        sub          = getattr(user, "subscription", None)
        quota        = sub.plan.storage_quota if sub else 500 * 1024 * 1024
        storage_pct  = min(100, round(storage_used / quota * 100)) if quota else 0

        return render(request, self.template_name, {
            "storage_used":  storage_used,
            "uploads_month": user.get_upload_count_this_month(),
            "storage_pct":   storage_pct,
        })

    def post(self, request):
        action = request.POST.get("action", "update_profile")
        if action == "update_profile":
            return self._update_profile(request)
        elif action == "change_password":
            return self._change_password(request)
        elif action == "delete_account":
            return self._delete_account(request)
        return redirect("profile")

    def _update_profile(self, request):
        user     = request.user
        username = request.POST.get("username", "").strip()
        avatar   = request.FILES.get("avatar")

        if username and username != user.username:
            if User.objects.filter(username=username).exclude(pk=user.pk).exists():
                messages.error(request, "That username is already taken.")
                return redirect("profile")
            user.username = username

        if avatar:
            user.avatar = avatar

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    def _change_password(self, request):
        user          = request.user
        old_password  = request.POST.get("old_password", "")
        new_password  = request.POST.get("new_password", "")
        new_password2 = request.POST.get("new_password2", "")

        if not user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("profile")

        if len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters.")
            return redirect("profile")

        if new_password != new_password2:
            messages.error(request, "New passwords do not match.")
            return redirect("profile")

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)   # stay logged in
        messages.success(request, "Password changed successfully.")
        return redirect("profile")

    def _delete_account(self, request):
        user = request.user
        from apps.files.models import File
        for f in File.objects.filter(owner=user):
            f.file.delete(save=False)
            f.delete()
        logout(request)
        user.delete()
        messages.info(request, "Your account has been deleted.")
        return redirect("home")