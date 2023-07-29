from django.urls import include, path

urlpatterns = [
    path("v1/", include("communications.ops.v1.urls")),
]
