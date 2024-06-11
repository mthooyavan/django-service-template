from django.conf import settings


class MasterSlaveRouter:
    @staticmethod
    def _is_not_silk_model(model):
        """Check if the model belongs to the Django Silk app."""
        return model._meta.app_label != "silk"

    def db_for_read(self, model, **_hints):
        return (
            "slave"
            if "slave" in settings.DATABASES and self._is_not_silk_model(model)
            else "default"
        )

    @staticmethod
    def db_for_write(_model, **_hints):
        return "default"

    @staticmethod
    def allow_relation(_obj1, _obj2, **_hints):
        return True

    @staticmethod
    def allow_migrate(db, _app_label, _model_name=None, **_hints):
        return db == "default"
