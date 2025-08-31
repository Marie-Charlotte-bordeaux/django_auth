from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.conf import settings
from django.conf import settings
from django.db.models import Q


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # met aussi à jour last_password_change (voir override ci-dessous)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email=email, password=password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff=True requis pour un superuser')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser=True requis pour un superuser')
        return self._create_user(email=email, password=password, **extra_fields)


class User(AbstractUser):
    # On supprime le champ username et on utilise l'email à la place
    username = None
    email = models.EmailField('email address', unique=True)

    # Suivi sécurité / brute force
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login_at = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)

    # Audit
    last_password_change = models.DateTimeField(default=timezone.now)
    email_verified = models.BooleanField(default=False)

    # paramètres de fenêtre/verrouillage (exigences du TP)
    FAILED_WINDOW_MINUTES = 30
    LOCK_MINUTES = 30
    FAILED_LIMIT = 5

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # pas de username

    objects = CustomUserManager()

    def set_password(self, raw_password):
        super().set_password(raw_password)
        # marquer l’instant du changement
        self.last_password_change = timezone.now()

    def register_failed_login(self):
        now = timezone.now()
        if self.last_failed_login_at and (now - self.last_failed_login_at).total_seconds() > self.FAILED_WINDOW_MINUTES * 60:
            # fenêtre expirée → on repart à zéro
            self.failed_login_attempts = 0
        self.failed_login_attempts += 1
        self.last_failed_login_at = now
        if self.failed_login_attempts >= self.FAILED_LIMIT:
            self.account_locked_until = now + timezone.timedelta(minutes=self.LOCK_MINUTES)

    def reset_failed_logins(self):
        self.failed_login_attempts = 0
        self.last_failed_login_at = None
        self.account_locked_until = None


class Document(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("publish_document", "Can publish documents"),
            ("review_document", "Can review documents"),
        ]

    def user_can_edit(self, user):
        return user.is_authenticated and (user == self.owner or user.has_perm('accounts.change_document'))

    def user_can_delete(self, user):
        return user.is_authenticated and (user == self.owner or user.has_perm('accounts.delete_document'))
