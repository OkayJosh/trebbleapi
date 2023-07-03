from rest_framework.viewsets import ModelViewSet

from brand.models import Brand, BrandPostTemplate
from brand.serializers import BrandSerializers, BrandPostTemplateSerializers
from trebbleapi.mixins import PermissionMixinAdmin


# Create your views here.
class BrandViewSet(PermissionMixinAdmin, ModelViewSet):
    serializer_class = BrandSerializers
    filterset_fields = ['uuid']
    lookup_url_kwarg = 'uuid'

    def get_queryset(self):
        return Brand.objects.order_by('-created')


class BrandPostTemplateViewSet(PermissionMixinAdmin, ModelViewSet):
    serializer_class = BrandPostTemplateSerializers
    filterset_fields = ['uuid']
    lookup_url_kwarg = 'uuid'

    def get_queryset(self):
        return BrandPostTemplate.objects.order_by('-created')
