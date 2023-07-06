from django.urls import path

from users.views import ExchangeSessionForToken

urlpatterns = [
    path('exchange/', ExchangeSessionForToken.as_view(), name='exchange_session_for_token'),
]
