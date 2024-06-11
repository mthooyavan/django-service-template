from django.urls import include, path
from rest_framework.routers import SimpleRouter

app_name = "api"

router = SimpleRouter()
urlpatterns = router.urls

urlpatterns += [
    # Include v1 communications urls
    path("v1/communications/", include("communications.api.v1.urls")),
]
