import logging

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from backend_service.logging import thread_local_storage


class LoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.logger = logging.getLogger("default")

    def process_request(self, request):
        self.logger.info(
            "Incoming request: Correlation ID: %s | Method: %s | Path: %s | Request Received Time: %s",
            request.correlation_id,
            request.method,
            request.path,
            thread_local_storage.request_initiated_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def process_response(self, request, response):
        thread_local_storage.request_processed_time = timezone.now()
        thread_local_storage.request_time_taken = (
            thread_local_storage.request_processed_time
            - thread_local_storage.request_initiated_time
        ).total_seconds() * 1000  # in milliseconds
        # Round off to 2 decimal places
        thread_local_storage.request_time_taken = round(
            thread_local_storage.request_time_taken, 2
        )
        response["X-Correlation-ID"] = request.correlation_id
        self.logger.info(
            "Outgoing response: Correlation ID: %s | Status: %s | Response Sent Time: %s | Time Taken: %s ms",
            request.correlation_id,
            response.status_code,
            thread_local_storage.request_processed_time.strftime("%Y-%m-%d %H:%M:%S"),
            thread_local_storage.request_time_taken,
        )
        return response
