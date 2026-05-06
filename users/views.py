"""
Представления для приложения users.
Обрабатывают регистрацию, вход, профиль пользователя и смену пароля.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator

from .forms import RegisterForm, LoginForm, EditProfileForm
from .models import User


def edit_profile_redirect(request):
    if request.user.is_authenticated:
        return redirect('users:edit_profile', user_id=request.user.id)
    return redirect('users:login')


def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('projects:project_list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Авторизация пользователя"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            return redirect('projects:project_list')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Выход из аккаунта"""
    logout(request)
    return redirect('projects:project_list')


def user_detail_view(request, user_id):
    """Страница профиля пользователя"""
    user_obj = get_object_or_404(User, id=user_id, is_active=True)
    projects = user_obj.owned_projects.all().order_by('-created_at')
    context = {
        'user': user_obj,
        'projects': projects,
    }
    return render(request, 'users/user-details.html', context)


@login_required
def edit_profile_view(request, user_id):
    """Редактирование профиля (доступно только владельцу)"""
    if request.user.id != user_id:
        return redirect('users:user_detail', user_id=request.user.id)

    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user_obj)
        if form.is_valid():
            form.save()
            return redirect('users:user_detail', user_id=user_obj.id)
    else:
        form = EditProfileForm(instance=user_obj)

    context = {
        'form': form,
        'user': user_obj,
    }
    return render(request, 'users/edit_profile.html', context)


@login_required
def change_password_view(request):
    """Смена пароля"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('users:user_detail', user_id=request.user.id)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


def users_list(request):
    """
    Список всех пользователей с фильтрацией.

    Доступные фильтры:
    authors_of_favorites: авторы избранных проектов
    authors_of_my_participated: авторы проектов, где я участвую
    users_who_like_my_projects: пользователи, которым нравятся мои проекты
    participants_of_my_projects: участники моих проектов
    """
    users_list = User.objects.filter(is_active=True).order_by('-id')
    active_filter = request.GET.get('filter')
    filter_title = None

    if request.user.is_authenticated and active_filter:
        if active_filter == 'authors_of_favorites':
            favorite_projects = request.user.favorites.all()
            author_ids = favorite_projects.values_list('owner_id', flat=True).distinct()
            users_list = User.objects.filter(id__in=author_ids)
            filter_title = 'Авторы избранных проектов'

        elif active_filter == 'authors_of_my_participated':
            participated_projects = request.user.participated_projects.all()
            author_ids = participated_projects.values_list('owner_id', flat=True).distinct()
            users_list = User.objects.filter(id__in=author_ids)
            filter_title = 'Авторы проектов, в которых я участвую'

        elif active_filter == 'users_who_like_my_projects':
            my_projects = request.user.owned_projects.all()
            user_ids = User.objects.filter(
                favorites__in=my_projects
            ).exclude(id=request.user.id).values_list('id', flat=True).distinct()
            users_list = User.objects.filter(id__in=user_ids)
            filter_title = 'Пользователи, которым нравятся мои проекты'

        elif active_filter == 'participants_of_my_projects':
            my_projects = request.user.owned_projects.all()
            user_ids = User.objects.filter(
                participated_projects__in=my_projects
            ).exclude(id=request.user.id).values_list('id', flat=True).distinct()
            users_list = User.objects.filter(id__in=user_ids)
            filter_title = 'Участники моих проектов'

    paginator = Paginator(users_list, 12)
    page_number = request.GET.get('page')
    participants = paginator.get_page(page_number)

    context = {
        'participants': participants,
        'active_filter': active_filter,
        'filter_title': filter_title,
    }
    return render(request, 'users/participants.html', context)
