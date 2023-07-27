from django.urls import path, include
import django.contrib.auth.views as auth_views
from .views import dashboard, register


urlpatterns = [
    # login-logout urls
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', include('django.contrib.auth.urls')),
    path('', dashboard, name='dashboard'),
    path('register/', register, name='register')
]
