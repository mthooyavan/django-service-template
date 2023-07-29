from django.urls import include, path

urlpatterns = [
    path('api/', include('engineering.api.urls')),

    path('health/', include('health_check.urls')),
]
