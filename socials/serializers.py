import os
import random
import string

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from socials.models import SocialPost


class PostSerializer(serializers.Serializer):
    account = serializers.IntegerField(required=True)
    image = serializers.FileField(required=False)
    message = serializers.CharField()

    def validate_image(self, value):
        if value is not None and value.size > 5242880:
            raise serializers.ValidationError('File size cannot exceed 5MB.')
        return value

    def validate_account(self, value):
        try:
            return SocialAccount.objects.get(id=value)
        except SocialPost.DoesNotExist:
            raise serializers.ValidationError('Social Account does not exist')

    def save(self):
        message = self.validated_data['message']
        account = self.validated_data['account']
        image = self.validated_data.get('image')

        if image:
            chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
            file_name = f"{account.id}_{image.name}_{''.join(random.choice(chars) for _ in range(10))}"
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            with open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            file_url = os.path.join(settings.MEDIA_URL, file_name)
        else:
            file_url = None

        return file_url


class SocialPostSerializers(ModelSerializer):
    class Meta:
        model = SocialPost
        fields = [
            'uuid', 'account', 'date_published',
            'content', 'file', 'likes',
            'comments', 'shares', 'published',
            'response', 'header', 'data'
        ]


