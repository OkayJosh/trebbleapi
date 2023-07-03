from django.urls import path

from socials.views import LinkedInPostView, ListPost

urlpatterns = [
    path('linkedin/', LinkedInPostView.as_view(), name='linkedin_post_action'),
    path('list/', ListPost.as_view(), name='linkedin_post_action'),
]