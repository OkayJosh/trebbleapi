from rest_framework.viewsets import ModelViewSet

from brand.models import Brand, BrandPostTemplate
from brand.serializers import BrandSerializers, BrandPostTemplateSerializers
from trebbleapi.permissions import IsUserOrReadOnly


# Create your views here.
class BrandViewSet(ModelViewSet):
    serializer_class = BrandSerializers
    permission_classes = [IsUserOrReadOnly, ]
    filterset_fields = ['uuid']
    lookup_url_kwarg = 'uuid'

    def get_queryset(self):
        return Brand.objects.order_by('-created')


class BrandPostTemplateViewSet(ModelViewSet):
    serializer_class = BrandPostTemplateSerializers
    filterset_fields = ['uuid']
    lookup_url_kwarg = 'uuid'
    permission_classes = [IsUserOrReadOnly, ]

    def get_queryset(self):
        return BrandPostTemplate.objects.order_by('-created')
