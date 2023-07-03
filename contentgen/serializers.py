from rest_framework import serializers

from brand.models import Brand


class ContentGeneratorSerializer(serializers.Serializer):
    number = serializers.IntegerField(default=1)
    brand = serializers.CharField()
    template = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super(ContentGeneratorSerializer, self).__init__(*args, **kwargs)
        print(self.context, 'self.context')
        self.user = self.context['request'].user
        self.business = self.context['request'].business

    def get_brand_choices(self):
        brands = self.business.brand_businesses.all()
        return [(brand.name.upper(), brand.name) for brand in brands]

    def get_template_choices(self, brand_name):
        brand = Brand.objects.filter(name=brand_name).first()
        if brand:
            templates = brand.brand_post_templates.all()
            return [(template.name.upper(), template.name) for template in templates]
        return []

    def validate_brand(self, value):
        brand = Brand.objects.filter(name=value).first()
        if not brand:
            raise serializers.ValidationError("Invalid brand name")
        return brand

    def validate_template(self, value):
        brand_name = self.initial_data.get('brand')
        if brand_name:
            brand = Brand.objects.filter(name=brand_name).first()
            if brand:
                template = brand.brand_post_templates.filter(name=value).first()
                if not template:
                    raise serializers.ValidationError("Invalid template name for the selected brand")
                return template
        raise serializers.ValidationError("Brand name is required")
