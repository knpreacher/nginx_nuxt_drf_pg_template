from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "is_staff")


class EmailTokenObtainSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD  # это "email"
