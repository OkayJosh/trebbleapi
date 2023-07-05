from copy import copy

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from brand.models import Brand, BrandPostTemplate
from brand.serializers import BrandSerializers, BrandPostTemplateSerializers
from trebbleapi.permissions import IsUserOrReadOnly


# Create your views here.
class BrandViewSet(ModelViewSet):
    serializer_class = BrandSerializers
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['uuid']
    lookup_url_kwarg = 'uuid'

    def get_queryset(self):
        return Brand.objects.order_by('-created')

    def create(self, request, *args, **kwargs):
        data = copy(request.data)
        data['user'] = request.user.uuid
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BrandPostTemplateViewSet(ModelViewSet):
    serializer_class = BrandPostTemplateSerializers
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['uuid']
    lookup_url_kwarg = 'uuid'

    def get_queryset(self):
        return BrandPostTemplate.objects.order_by('-created')
