from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('', include('users.urls')),
    path('content/', include('contentgen.urls')),
    path('brand/', include('brand.urls')),
    path('post/', include('socials.urls')),
    path('', include('linkedin_oauth2.urls')),
    path('account/', include('allauth.account.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
