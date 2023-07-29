from django.urls import path, include


urlpatterns = [
    path('v1/', include('engineering.api.v1.urls')),
]
