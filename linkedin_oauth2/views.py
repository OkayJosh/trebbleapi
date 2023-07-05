from datetime import timedelta

import requests
from allauth.account.models import EmailAddress

from allauth.socialaccount import app_settings
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from allauth.socialaccount.providers.base import ProviderException
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from django.utils import timezone
from rest_framework.authtoken.models import Token

from linkedin_oauth2.provider import LinkedInOAuth2Provider, _extract_email, _extract_name_field
from rest_framework.views import APIView
from rest_framework.response import Response

from users.models import User


class LinkedInOAuth2Adapter(OAuth2Adapter):
    provider_id = LinkedInOAuth2Provider.id
    access_token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    authorize_url = "https://www.linkedin.com/oauth/v2/authorization"
    profile_url = "https://api.linkedin.com/v2/me"
    email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"  # noqa
    # See:
    # http://developer.linkedin.com/forum/unauthorized-invalid-or-expired-token-immediately-after-receiving-oauth2-token?page=1 # noqa
    access_token_method = "GET"

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_user_info(token)
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_user_info(self, token):
        fields = self.get_provider().get_profile_fields()

        headers = {}
        headers.update(self.get_provider().get_settings().get("HEADERS", {}))
        headers["Authorization"] = " ".join(["Bearer", token.token])

        info = {}
        if app_settings.QUERY_EMAIL:
            resp = requests.get(self.email_url, headers=headers)
            # If this response goes wrong, that is not a blocker in order to
            # continue.
            if resp.ok:
                info = resp.json()

        url = self.profile_url + "?projection=(%s)" % ",".join(fields)
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        info.update(resp.json())
        return info


oauth2_login = OAuth2LoginView.adapter_view(LinkedInOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(LinkedInOAuth2Adapter)


class LinkedInOAuth2APIView(APIView):
    provider_id = LinkedInOAuth2Provider.id
    profile_url = "https://api.linkedin.com/v2/me"
    email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"  # noqa

    def get(self, request):
        # Get the authorization code from the request query parameters
        access_token = request.headers.get('Authorization', None)
        # Make an API request using the access token
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = requests.get(self.profile_url, headers=headers)
        profile_response.raise_for_status()
        profile_data = profile_response.json()

        email_info = {}
        if app_settings.QUERY_EMAIL:
            email_response = requests.get(self.email_url, headers=headers)
            if email_response.ok:
                email_info = email_response.json()

        # Combine the profile data and email info
        user_info = profile_data.copy()
        user_info.update(email_info)
        dync = {'channel': 'linkedin', 'account_type': 'BASIC',
                'last_login': timezone.now()}

        # user account creation and set up
        user_object, created = User.objects.get_or_create(email=_extract_email(email_info),
                                                          defaults=self.extract_common_fields(user_info))
        for key, value in dync.items():
            setattr(user_object, key, value)
        user_object.save()
        EmailAddress.objects.get_or_create(email=user_object.email, defaults={
            'email': user_object.email, 'user': user_object.uuid, 'primary': True, 'verified': True
        })
        account, _created = SocialAccount.objects.get_or_create(uid=self.extract_uid(user_info), defaults={
            'provider': 'linkedin_oauth2', 'last_login': timezone.now(), 'date_joined': timezone.now(),
            'user': user_object.uuid, 'extra_data': user_info
        })
        SocialToken.objects.get_or_create(account=account, app=SocialApp.objects.filter(provider='linkedin_oauth2').last(),  defaults={
            'token': access_token, 'expires_at': timezone.now() + timedelta(seconds=10000)
        })
        token, _created = Token.objects.get_or_create(user=user_object)
        user_info.update({
            'token': token.key,
            'device_name': 'Linkedin Exchange'})
        return Response(user_info)

    def extract_common_fields(self, data):
        return dict(
            first_name=_extract_name_field(data, "firstName"),
            last_name=_extract_name_field(data, "lastName"),
            email=_extract_email(data),
        )

    def extract_uid(self, data):
        if "id" not in data:
            raise ProviderException(
                "LinkedIn encEmailAddressountered an internal error while logging in. \
                Please try again."
            )
        return str(data["id"])