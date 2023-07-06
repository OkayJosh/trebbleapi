from rest_framework import serializers

from brand.models import Brand


class ContentGeneratorSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    brand = serializers.CharField()
    template = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super(ContentGeneratorSerializer, self).__init__(*args, **kwargs)
        self.user = self.context['request'].user

    def get_brand_choices(self):
        brands = self.user.user_brands.all()
        return [(brand.name.upper(), brand.name) for brand in brands]

    def get_template_choices(self, brand_name):
        brand = Brand.objects.get(name=brand_name).first()
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
        uuid = self.initial_data.get('uuid')
        if uuid:
            brand = Brand.objects.filter(uuid=uuid).first()
            if brand:
                template = brand.brand_post_templates.filter(name=value).first()
                if not template:
                    raise serializers.ValidationError("Invalid template name for the selected brand")
                return template
        raise serializers.ValidationError("Brand name is required")
