from rest_framework.serializers import ModelSerializer

from brand.models import Brand, BrandPostTemplate


class BrandSerializers(ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            'name', 'logo',
            'description', 'product_description',
            'contact_number', 'website_url', 'numbers_of_daily_post',
        ]


class BrandPostTemplateSerializers(ModelSerializer):
    class Meta:
        model = BrandPostTemplate
        fields = [
            'name', 'brand',
            'header', 'body', 'footer'
        ]
