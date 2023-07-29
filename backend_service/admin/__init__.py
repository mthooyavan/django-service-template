from django.contrib.admin.apps import AdminConfig as DJAdminConfig


class AdminConfig(DJAdminConfig):
    default_site = "backend_service.admin.site.AdminSite"
