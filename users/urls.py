"""
Маршруты для приложения users
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('list/', views.users_list, name='users_list'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('edit-profile/', views.edit_profile_redirect, name='edit_profile_redirect'),
    path('<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('<int:user_id>/edit/', views.edit_profile_view, name='edit_profile'),
]
