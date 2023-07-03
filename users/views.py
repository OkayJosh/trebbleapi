import logging
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView


LOG = logging.getLogger(__name__)

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view=None):
        if request.method in SAFE_METHODS:
            return True
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsUserOrReadOnly(BasePermission):
    def has_permission(self, request, view=None):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user)


class PermissionMixinAdmin:
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = 9
    pagination_class.limit_query_param = 'page_size'
    pagination_class.offset_query_param = 'page'

    def get_permissions(self):
        permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
        if self.action in ['create', 'post', 'delete']:
            permission_classes = [IsAdminOrReadOnly(), ]
        return permission_classes


class PermissionMixinUser(PermissionMixinAdmin):
    def get_permissions(self):
        permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
        if self.action in ['create', 'post']:
            permission_classes = [IsUserOrReadOnly(), ]
        elif self.action in ['delete']:
            permission_classes = [IsAdminOrReadOnly, ]
        return permission_classes


class CustomThrottle(SimpleRateThrottle):
    scope = 'custom'
    rate = '10/day'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class ThrottleMixin:
    throttle_classes = [CustomThrottle]

    def get_throttles(self):
        if self.request.user and self.request.user.is_authenticated:
            self.throttle_classes = []
        return [throttle() for throttle in self.throttle_classes]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Remove the device from the user's logged_devices list
        device_name = request.headers.get("Device-Name")
        device_id = request.headers.get("Device-Id")
        device = request.user.logged_devices.filter(device_name=device_name, device_id=device_id).first()
        if device:
            device.delete()
            return Response({"message": "Device successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
