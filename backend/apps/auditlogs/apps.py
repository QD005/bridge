from django.apps import AppConfig


class AuditlogsConfig(AppConfig):
    name = 'apps.auditlogs'

    def ready(self):
        import apps.auditlogs.signals
