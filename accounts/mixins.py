from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.models import Group

class OwnerRequiredMixin(AccessMixin):
    owner_field = 'owner'  # override si besoin

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_authenticated or getattr(obj, self.owner_field) != request.user:
            return HttpResponseForbidden("Accès refusé.")
        return super().dispatch(request, *args, **kwargs)

class GroupRequiredMixin(AccessMixin):
    group_name = None  # à définir dans la vue

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.group_name and not request.user.groups.filter(name=self.group_name).exists():
            return HttpResponseForbidden("Groupe requis.")
        return super().dispatch(request, *args, **kwargs)
