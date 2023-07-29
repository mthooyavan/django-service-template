from django.urls import path

from communications.ops.v1.views import SendNotificationsView

urlpatterns = [
    path('ops/v3/notifications/<str:type>', SendNotificationsView.as_view(), name='ops_send_notifications'),
]
