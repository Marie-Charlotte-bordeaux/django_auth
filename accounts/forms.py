from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()

GENERIC_ERROR = "Email ou mot de passe incorrect."

class SecureLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")  # remplace l'étiquette

    def clean(self):
        cleaned = super().clean()  # garde la mécanique standard (inclut confirm_login_allowed)
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        # On gère nos règles
        now = timezone.now()
        user = None
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = None

        # Compte verrouillé ?
        if user and user.account_locked_until and user.account_locked_until > now:
            raise ValidationError(f"Compte temporairement verrouillé. Réessayez après {user.account_locked_until:%H:%M}.", code='locked')

        # Authentification
        authed = authenticate(self.request, username=email, password=password)
        if authed is None:
            # tentative échouée : on incrémente si l'email correspond à un compte
            if user:
                user.register_failed_login()
                user.save(update_fields=['failed_login_attempts', 'last_failed_login_at', 'account_locked_until'])
            raise ValidationError(GENERIC_ERROR, code='invalid_login')

        # Succès : reset des compteurs
        if user:
            user.reset_failed_logins()
            user.save(update_fields=['failed_login_attempts', 'last_failed_login_at', 'account_locked_until'])

        # stocker l'utilisateur pour la vue
        self.user_cache = authed
        return cleaned
