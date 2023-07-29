from django.urls import path, include


urlpatterns = [
    path('api/', include('engineering.api.urls')),

    path('health/', include('health_check.urls')),
]
