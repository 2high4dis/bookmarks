from django.urls import path, include
import django.contrib.auth.views as auth_views
from .views import dashboard, register, edit, user_list, user_detail, user_follow


urlpatterns = [
    # login-logout urls
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', include('django.contrib.auth.urls')),
    path('', dashboard, name='dashboard'),
    path('register/', register, name='register'),
    path('edit/', edit, name='edit'),
    path('users/', user_list, name='user_list'),
    path('users/follow/', user_follow, name='user_follow'),
    path('users/<username>/', user_detail, name='user_detail'),
]
