from django.urls import include, path

urlpatterns = [
    path('v1/', include('communications.api.v1.urls')),
]
