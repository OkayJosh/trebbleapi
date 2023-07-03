from celery import shared_task

from socials.views import LinkedInPostAdapter


@shared_task
def post_to_linkedin(access_token, message, handler=None, image_url=None, post_db_sync_id=None):
    adapter = LinkedInPostAdapter()
    adapter.authenticate(access_token)
    return adapter.post(message, handler, image_url, post_db_sync_id)
