from rest_framework.throttling import ScopedRateThrottle as DefaultScopedRateThrottle

from backend_service.exceptions import APIException, ThrottledAPIException
from utils.constants import CLIENT_THROTTLE_SCOPE


class ScopedRateThrottle(DefaultScopedRateThrottle):
    def __init__(self):
        super().__init__()
        self.request = None

    def get_rate(self):
        """
        Determine the string representation of the allowed request rate.
        """
        if not getattr(self, "scope", None):
            msg = f"You must set either `.scope` or `.rate` for '{self.__class__.__name__}' throttle"
            raise APIException(msg)

        if (
            self.scope == CLIENT_THROTTLE_SCOPE
            and self.request
            and hasattr(self.request, "user")
        ):
            return self.request.user.throttle_rate

        try:
            return self.THROTTLE_RATES[self.scope]
        except KeyError as exc:
            msg = f"No default throttle rate set for '{self.scope}' scope"
            raise APIException(msg) from exc

    def allow_request(self, request, view):
        """
        Override to send a custom response when throttling is necessary.
        """
        self.request = request
        if super().allow_request(request, view):
            return True

        raise ThrottledAPIException(wait=self.wait())
