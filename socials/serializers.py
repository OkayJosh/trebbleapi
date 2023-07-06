import os
import random
import string
from datetime import timedelta

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from socials.models import SocialPost


class PostSerializer(serializers.Serializer):
    account_uid = serializers.CharField(required=True)
    image = serializers.FileField(required=False)
    message = serializers.CharField()
    scheduled_time = serializers.DateTimeField(required=False)

    def validate_image(self, value):
        if value is not None and value.size > 5242880:
            raise serializers.ValidationError('File size cannot exceed 5MB.')
        return value

    def validate_message(self, value):
        if not value:
            raise serializers.ValidationError('Please include text')
        return value

    def validate_account_uid(self, value):
        try:
            return SocialAccount.objects.get(uid=value)
        except SocialPost.DoesNotExist:
            raise serializers.ValidationError('Social Account does not exist')

    def validate_scheduled_time(self, value):
        if value:
            if value < timezone.now() + timedelta(seconds=60):
                raise serializers.ValidationError('Make Sure your scheduled time is in the future for at least 1 minutes')
            else:
                return value
        else:
            return None

    def save(self):
        message = self.validated_data['message']
        account = self.validated_data['account_uid']
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


