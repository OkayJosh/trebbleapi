from django.urls import path

from contentgen.views import ContentGeneratorView

urlpatterns = [
    path('generate/', ContentGeneratorView.as_view(), name='generate_content'),
]