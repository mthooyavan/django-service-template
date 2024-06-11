from rest_framework import status
from rest_framework.response import Response
from backend_service.authentication import IPAddressAuthentication
from backend_service.exceptions import BadRequestExceptionAPIException
from backend_service.permissions import AllowAny

from communications.ops.v1.serializers import NotificationValidationSerializer
from communications.tasks.emails import send_notifications
from utils.views import APIView


class SendNotificationsView(APIView):
    authentication_classes = [IPAddressAuthentication]
    permission_classes = [AllowAny]
    swagger_schema = None

    def post(self, *args, **kwargs):
        if self.kwargs["type"] == "email":
            serializer = NotificationValidationSerializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.data
            send_notifications.delay(data)
            return Response(
                data={"message": "Notification request is being processed."},
                status=status.HTTP_200_OK,
            )

        raise BadRequestExceptionAPIException(
            detail="Invalid notifications request",
        )
