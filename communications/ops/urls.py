from django.urls import path, include


urlpatterns = [
    path('v1/', include('communications.ops.v1.urls')),
]
