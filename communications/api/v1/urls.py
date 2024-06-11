from rest_framework.routers import SimpleRouter

from communications.api.v1.viewsets import TemplateViewSet

app_name = "communications"

router = SimpleRouter()
router.register(r"templates", TemplateViewSet, basename="template")

urlpatterns = []

urlpatterns += router.urls
