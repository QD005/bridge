from django.apps import AppConfig


class ExecutionsConfig(AppConfig):
    name = 'apps.executions'

    def ready(self):
        import apps.executions.signals
