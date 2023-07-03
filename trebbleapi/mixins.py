from rest_framework.pagination import LimitOffsetPagination
from rest_framework.settings import api_settings

from trebbleapi.permissions import IsAdminOrReadOnly, IsUserOrReadOnly


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