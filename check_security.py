import django, sys
from django.conf import settings

def main():
    issues = []

    if getattr(settings, 'DEBUG', True):
        issues.append("DEBUG doit être False en production.")
    if getattr(settings, 'SECRET_KEY', 'dev-insecure-change-me') == 'dev-insecure-change-me':
        issues.append("SECRET_KEY par défaut, remplace-le par une vraie clé secrète.")
    if not getattr(settings, 'ALLOWED_HOSTS', []):
        issues.append("ALLOWED_HOSTS doit être configuré.")
    if not getattr(settings, 'SESSION_COOKIE_HTTPONLY', False):
        issues.append("SESSION_COOKIE_HTTPONLY devrait être True.")
    if not getattr(settings, 'CSRF_COOKIE_HTTPONLY', False):
        issues.append("CSRF_COOKIE_HTTPONLY devrait être True.")
    if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
        issues.append("SESSION_COOKIE_SECURE devrait être True en prod.")
    if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
        issues.append("CSRF_COOKIE_SECURE devrait être True en prod.")
    hashers = getattr(settings, 'PASSWORD_HASHERS', [])
    if not any('Argon2PasswordHasher' in h for h in hashers):
        issues.append("Argon2 devrait être activé comme hasher principal.")

    if issues:
        print("⚠️ Problèmes de configuration :")
        for i in issues:
            print("-", i)
        sys.exit(1)
    else:
        print("✅ Configuration de sécurité OK.")

if __name__ == "__main__":
    django.setup()
    main()
