from django.urls import include, path  # pylint: disable=unused-import

from communications.ops.v1.views import SendNotificationsView

app_name = "communications"

urlpatterns = [
    path(
        "notifications/<str:type>",
        SendNotificationsView.as_view(),
        name="ops_send_notifications",
    ),
]
