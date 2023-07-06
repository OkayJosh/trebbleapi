from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('v1/', include('users.urls')),
    path('v1/content/', include('contentgen.urls')),
    path('v1/brand/', include('brand.urls')),
    path('v1/post/', include('socials.urls')),
    path('v1/', include('linkedin_oauth2.urls')),
    path('v1/account/', include('allauth.account.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
