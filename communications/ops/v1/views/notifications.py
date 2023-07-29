from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from communications.ops.v1.serializers import NotificationValidationSerializer
from communications.tasks.emails import send_notifications
from backend_service import errors
from backend_service.authentication import IPAddressAuthentication
from backend_service.permissions import AllowAny


class SendNotificationsView(APIView):
    authentication_classes = [IPAddressAuthentication]
    permission_classes = [AllowAny]

    def post(self, *args, **kwargs):
        if self.kwargs['type'] == 'email':
            serializer = NotificationValidationSerializer(data=self.request.data)
            if serializer.is_valid():
                data = serializer.data
                send_notifications.delay(data)
                return Response(
                    data={"message": "Notification request is being processed."},
                    status=status.HTTP_200_OK
                )
            return errors.handle(serializer.errors, status.HTTP_400_BAD_REQUEST)

        return Response(
            data={"message": "Invalid notifications request"},
            status=status.HTTP_400_BAD_REQUEST
        )
