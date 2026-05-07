from django.apps import AppConfig


class MerchstoreConfig(AppConfig):
    name = 'merchstore'

    def ready(self):
        from . import signals  # noqa: F401
