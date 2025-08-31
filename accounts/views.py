from django.http import HttpResponseForbidden
from django.shortcuts import render

# Create your views here.
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import SecureLoginForm

from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Document
from .mixins import OwnerRequiredMixin, GroupRequiredMixin


class SecureLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = SecureLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        # Rotation explicite de session (anti fixation)
        self.request.session.flush()
        authed_user = form.get_user()
        auth_login(self.request, authed_user)

        # Alerte si mot de passe > 90 jours
        pwd_age = (timezone.now() - authed_user.last_password_change).days
        if pwd_age > 90:
            messages.warning(self.request, "Votre mot de passe a plus de 90 jours, pensez à le changer.")

        return redirect(self.get_success_url())

class SecureLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')



class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/list.html'

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('accounts.view_document'):
            return Document.objects.all()
        return Document.objects.filter(Q(is_public=True) | Q(owner=user))

class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    fields = ['title', 'content', 'is_public']
    template_name = 'documents/form.html'
    success_url = reverse_lazy('documents:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class DocumentUpdateView(OwnerRequiredMixin, UpdateView):
    model = Document
    fields = ['title', 'content', 'is_public']
    template_name = 'documents/form.html'
    success_url = reverse_lazy('documents:list')

class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'documents/detail.html'

class DocumentPublishView(GroupRequiredMixin, View):
    group_name = 'editors'

    def post(self, request, *args, **kwargs):

        from django.shortcuts import get_object_or_404, redirect
        doc = get_object_or_404(Document, pk=kwargs['pk'])
        if not request.user.has_perm('accounts.publish_document'):
            return HttpResponseForbidden("Permission manquante.")
        doc.is_public = True
        doc.save(update_fields=['is_public'])
        return redirect('documents:detail', pk=doc.pk)

