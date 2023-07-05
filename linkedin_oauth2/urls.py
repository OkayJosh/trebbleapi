from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from django.urls import path

from linkedin_oauth2.provider import LinkedInOAuth2Provider
from linkedin_oauth2.views import LinkedInOAuth2APIView

urlpatterns = default_urlpatterns(LinkedInOAuth2Provider)
urlpatterns += [
    path('linkedin_oauth2/api/', LinkedInOAuth2APIView.as_view(), name='linkedin_api_auth'),
]
