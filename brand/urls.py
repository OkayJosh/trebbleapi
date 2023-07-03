from django.urls import path, include
from rest_framework import routers

from brand.views import BrandViewSet, BrandPostTemplateViewSet

router = routers.DefaultRouter()
router.register(r'brands', BrandViewSet, basename='brands')
router.register(r'templates', BrandPostTemplateViewSet, basename='templates')


urlpatterns = [
    path('', include(router.urls)),
]