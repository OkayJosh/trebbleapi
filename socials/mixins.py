from datetime import datetime
from django.utils import timezone

from socials.tasks import post_to_linkedin


class ScheduleMixin:
    def schedule_post(self, access_token, post_db_sync_id, scheduled_time):
        if scheduled_time < timezone.now():
            raise ValueError('Scheduled time must be in the future')
        delay = (scheduled_time - timezone.now()).total_seconds()
        post_to_linkedin.apply_async(args=[access_token, post_db_sync_id], countdown=delay)
