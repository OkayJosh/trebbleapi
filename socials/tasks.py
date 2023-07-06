from celery import shared_task
from socials.models import SocialPost


@shared_task
def post_to_linkedin(access_token, post_db_sync_id=None):
    from socials.views import LinkedInPostAdapter
    adapter = LinkedInPostAdapter()
    adapter.authenticate(access_token)
    social_post = SocialPost.objects.get(uuid=post_db_sync_id)
    return adapter.post(message=social_post.content, handler=None,
                        image_url=social_post.file.url, post_db_sync_id=post_db_sync_id)
