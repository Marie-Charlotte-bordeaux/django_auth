from django.urls import path
from .views import  (
    SecureLoginView, SecureLogoutView,
    DocumentListView, DocumentCreateView, DocumentUpdateView, DocumentDetailView, DocumentPublishView
)
from django.contrib.auth import views as auth_views


app_name = 'accounts'

urlpatterns = [
    #path('login/', SecureLoginView.as_view(), name='login'),
    #path('logout/', SecureLogoutView.as_view(), name='logout'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("login/", auth_views.LoginView.as_view(), name="login"),

# documents
    path('documents/', DocumentListView.as_view(), name='documents_list'),
    path('documents/create/', DocumentCreateView.as_view(), name='documents:create'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='documents:detail'),
    path('documents/<int:pk>/edit/', DocumentUpdateView.as_view(), name='documents:edit'),
    path('documents/<int:pk>/publish/', DocumentPublishView.as_view(), name='documents:publish'),



]
