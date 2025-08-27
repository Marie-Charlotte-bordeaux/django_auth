from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # importe handlers de signaux (login failed / login success)
        import accounts.signals  # noqa: F401