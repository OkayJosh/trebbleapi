import requests
from allauth.socialaccount.models import SocialAccount
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from linkedin_oauth2.provider import LinkedInOAuth2Provider
from socials.adapters import PostAdapter
from socials.mixins import ScheduleMixin
from socials.models import SocialPost
from socials.serializers import PostSerializer, SocialPostSerializers
from trebbleapi.throttles import CustomThrottle


class LinkedInPostAdapter(PostAdapter, ScheduleMixin):
    provider_id = LinkedInOAuth2Provider.id
    API_URL = 'https://api.linkedin.com/v2/ugcPosts'
    MEDIA_UPLOAD_URL = 'https://api.linkedin.com/v2/assets?action=registerUpload'
    MAX_IMAGE_SIZE = 5_242_880  # 5 MB

    def __init__(self):
        self.access_token = None
        self.account = None

    def authenticate(self, account, access_token=None):
        self.account = account
        self.access_token = access_token if access_token else self.account.socialtoken_set.first().token
        if access_token and not account:
            self.account = SocialAccount.objects.filter(extra_data__access_token=access_token)

    def post_async(self, message, scheduled_time=None, handler=None, image_url=None):
        post_db_sync = SocialPost.objects.create(content=message, date_published=scheduled_time or timezone.now(),
                                                 file=image_url, account=self.account)
        if scheduled_time:
            self.schedule_post(access_token=self.access_token,
                               scheduled_time=scheduled_time, post_db_sync_id=post_db_sync.uuid)
        else:
            self.post(message=message, handler=handler, image_url=image_url, post_db_sync_id=post_db_sync.uuid)
        return 'Submitted'

    def post(self, message, handler=None, image_url=None, post_db_sync_id=None):
        handler = handler if handler else f"urn:li:person:{self.account.extra_data['id']}"
        media_id = None

        # If post contains an image, upload it to LinkedIn and get media ID
        if image_url:
            media_id = self._upload_media(image_url)

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
        }
        data = {
            'author': handler,
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': message,
                    },
                    'shareMediaCategory': 'NONE',
                },
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC',
            },
        }

        # Add media ID to post data if available
        if media_id:
            data['specificContent']['com.linkedin.ugc.ShareContent']['media'] = [{
                'status': 'READY',
                'media': media_id,
            }]

        response = requests.post(self.API_URL, headers=headers, json=data)
        response.raise_for_status()
        post = SocialPost.objects.get(uuid=post_db_sync_id)
        post.response = response.json()
        post.published = True
        post.date_published = timezone.now()
        post.save()
        return response

    def _upload_media(self, image_url):
        # Download image
        response = requests.get(image_url)
        response.raise_for_status()

        # Check image size
        if len(response.content) > self.MAX_IMAGE_SIZE:
            raise ValueError('Image exceeds maximum size')

        # Prepare upload headers
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/octet-stream',
            'X-Restli-Protocol-Version': '2.0.0',
            'X-Upload-Content-Type': 'image/jpeg',
            'X-Upload-Content-Length': str(len(response.content)),
        }

        # Initiate upload
        upload_response = requests.post(self.MEDIA_UPLOAD_URL, headers=headers)
        upload_response.raise_for_status()

        # Upload image data
        upload_url = upload_response.json()['value']['uploadMechanism'][
            'com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        response = requests.put(upload_url, headers=headers, data=response.content)
        response.raise_for_status()

        # Complete upload
        complete_url = upload_response.json()['value']['completeUploadRequest']['uploadUrl']
        complete_response = requests.post(complete_url, headers=headers)
        complete_response.raise_for_status()

        # Return media ID
        return complete_response.json()['value']['id']


class LinkedInPostView(CustomThrottle, APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    adapter = LinkedInPostAdapter

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            adapter = self.adapter()
            adapter.authenticate(account=serializer.validated_data['account_uid'])
            # if not serializer.validated_data['scheduled_time']:
            adapter_response = adapter.post_async(message=serializer.validated_data['message'],
                                                  scheduled_time=serializer.validated_data.get('scheduled_time', None),
                                                  image_url=serializer.save())
            return Response({'message': 'Post successful', 'response': adapter_response}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListPost(CustomThrottle, ListAPIView):
    serializer_class = SocialPostSerializers
    lookup_field = 'uuid'
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SocialPost.objects.filter(account__user=self.request.user)

