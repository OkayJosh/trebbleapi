import logging

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialToken
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


LOG = logging.getLogger(__name__)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Remove the device from the user's logged_devices list
        device_name = request.headers.get("Device-Name")
        device_id = request.headers.get("Device-Id")
        device = request.user.logged_devices.filter(device_name=device_name, device_id=device_id).first()
        if device:
            device.delete()
            return Response({"message": "Device successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)


class ExchangeSessionForToken(APIView):
    def get(self, request):
        # Check if the user is authenticated using a session
        if request.user.is_authenticated:
            token, created = Token.objects.get_or_create(user=request.user)
            try:
                email = EmailAddress.objects.get(user=request.user).email
            except EmailAddress.DoesNotExist:
                email = request.user.email if request.user.email else 'Please set your email'

            return Response({
                'token': token.key,
                'user_uid': request.user.pk,
                'email': email,
                'device_name': 'Exchange',
                # 'expires': token.expires,
            })
        else:
            # If the user is not authenticated, return an error response
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        access_token = request.data.get('access_token')
        # print('access_token', access_token)
        # print('access_token': access_token)
        if not access_token:
            return Response({'error', 'Invalid Access token'}, status=status.HTTP_400_BAD_REQUEST)

        social_token = SocialToken.objects.filter(token=access_token).last()
        user = social_token.account.user
        token, created = Token.objects.get_or_create(user=user)
        try:
            email = EmailAddress.objects.get(user=user).email
        except EmailAddress.DoesNotExist:
            email = request.user.email if request.user.email else 'Please set your email'

        return Response({
            'token': token.key,
            'user_uid': user.pk,
            'email': email,
            'device_name': 'Exchange',
        })
