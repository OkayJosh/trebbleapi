from rest_framework.serializers import ModelSerializer

from brand.models import Brand


class BrandSerializers(ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            'uuid', 'name', 'logo',
            'descriptions', 'product_description',
            'contact_number', 'website_url', 'numbers_of_daily_post',
        ]


class BrandPostTemplateSerializers(ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            'uuid', 'name', 'brand',
            'header', 'body', 'footer'
        ]
