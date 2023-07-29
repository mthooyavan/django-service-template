from django.urls import include, path

urlpatterns = [
    path("v1/", include("engineering.api.v1.urls")),
]
