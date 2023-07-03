from datetime import datetime
from django.utils import timezone


class ScheduleMixin:
    def schedule_post(self, headers, data, scheduled_time):
        scheduled_time = datetime.fromisoformat(scheduled_time)
        if scheduled_time < timezone.now():
            raise ValueError('Scheduled time must be in the future')
        # TODO: warn the user if at the schedule time the current access_token would have expired
        # TODO: log warning mail to remind the to reauthenticate before then
        # delay = (scheduled_time - now).total_seconds()
        # self.post_later(headers, data, delay)
