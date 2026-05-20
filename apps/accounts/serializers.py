from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ["email", "username", "password", "password2"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    storage_used   = serializers.SerializerMethodField()
    uploads_month  = serializers.SerializerMethodField()
    plan           = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ["id", "email", "username", "avatar",
                  "created_at", "storage_used", "uploads_month", "plan"]

    def get_storage_used(self, obj):
        return obj.get_storage_used()

    def get_uploads_month(self, obj):
        return obj.get_upload_count_this_month()

    def get_plan(self, obj):
        sub = getattr(obj, "subscription", None)
        return sub.plan.name if sub else "Free"