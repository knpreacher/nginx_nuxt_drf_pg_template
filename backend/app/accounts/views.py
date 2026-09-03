from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import EmailTokenObtainSerializer, UserSerializer


def _set_cookie(response, key, value, max_age):
    response.set_cookie(
        key, value,
        max_age=max_age,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        domain=settings.JWT_COOKIE_DOMAIN,
        path="/",
    )


def _access_max_age():
    return int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())


def _refresh_max_age():
    return int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())


class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        data = serializer.validated_data
        resp = Response(UserSerializer(serializer.user).data)
        _set_cookie(resp, settings.JWT_ACCESS_COOKIE, data["access"], _access_max_age())
        _set_cookie(resp, settings.JWT_REFRESH_COOKIE, data["refresh"], _refresh_max_age())
        return resp


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        if not raw:
            raise InvalidToken("No refresh cookie")
        try:
            refresh = RefreshToken(raw)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        resp = Response({"detail": "refreshed"})
        _set_cookie(resp, settings.JWT_ACCESS_COOKIE, str(refresh.access_token), _access_max_age())
        return resp


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        resp = Response({"detail": "logged out"})
        resp.delete_cookie(settings.JWT_ACCESS_COOKIE, path="/", domain=settings.JWT_COOKIE_DOMAIN)
        resp.delete_cookie(settings.JWT_REFRESH_COOKIE, path="/", domain=settings.JWT_COOKIE_DOMAIN)
        return resp


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
