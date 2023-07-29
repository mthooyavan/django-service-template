from django.urls import path, include


urlpatterns = [
    path('v1/', include('communications.api.v1.urls')),
]
