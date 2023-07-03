from rest_framework.throttling import SimpleRateThrottle


class CustomThrottle(SimpleRateThrottle):
    scope = 'custom'
    rate = '10/day'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class ThrottleMixin:
    throttle_classes = [CustomThrottle]

    def get_throttles(self):
        if self.request.user and self.request.user.is_authenticated:
            self.throttle_classes = []
        return [throttle() for throttle in self.throttle_classes]