"""
Представления для приложения users.
Обрабатывают регистрацию, вход, профиль пользователя и смену пароля.
"""

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from constants import PAGINATION_PAGE_SIZE

from .forms import EditProfileForm, LoginForm, RegisterForm
from .models import User


def paginate_queryset(queryset, page_number, page_size=PAGINATION_PAGE_SIZE):
    """Универсальная функция пагинации"""
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(page_number)


def edit_profile_redirect(request):
    if request.user.is_authenticated:
        return redirect('users:edit_profile', user_id=request.user.id)
    return redirect('users:login')


def register_view(request):
    """Регистрация нового пользователя"""
    if request.method != 'POST':
        form = RegisterForm()
        return render(request, 'users/register.html', {'form': form})

    form = RegisterForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'users/register.html', {'form': form})

    user = form.save()
    login(request, user)
    return redirect('projects:project_list')


def login_view(request):
    """Авторизация пользователя"""
    if request.method != 'POST':
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

    form = LoginForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'users/login.html', {'form': form})

    user = form.user
    login(request, user)
    return redirect('projects:project_list')


def logout_view(request):
    """Выход из аккаунта"""
    logout(request)
    return redirect('projects:project_list')


def user_detail_view(request, user_id):
    """Страница профиля пользователя"""
    user = get_object_or_404(User, id=user_id, is_active=True)
    projects = (
        user.owned_projects
        .select_related('owner')
        .prefetch_related('participants')
    )
    context = {
        'user': user,
        'projects': projects,
    }
    return render(request, 'users/user-details.html', context)


@login_required
def edit_profile_view(request, user_id):
    """Редактирование профиля (доступно только владельцу)"""
    if request.user.id != user_id:
        return redirect('users:user_detail', user_id=request.user.id)

    user = get_object_or_404(User, id=user_id)

    if request.method != 'POST':
        form = EditProfileForm(instance=user)
        context = {'form': form, 'user': user}
        return render(request, 'users/edit_profile.html', context)

    form = EditProfileForm(request.POST, request.FILES, instance=user)
    if not form.is_valid():
        context = {'form': form, 'user': user}
        return render(request, 'users/edit_profile.html', context)

    form.save()
    return redirect('users:user_detail', user_id=user.id)


@login_required
def change_password_view(request):
    """Смена пароля"""
    if request.method != 'POST':
        form = PasswordChangeForm(request.user)
        return render(request, 'users/change_password.html', {'form': form})

    form = PasswordChangeForm(request.user, request.POST)
    if not form.is_valid():
        return render(request, 'users/change_password.html', {'form': form})

    user = form.save()
    update_session_auth_hash(request, user)
    return redirect('users:user_detail', user_id=request.user.id)


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

    page_number = request.GET.get('page', 1)
    participants = paginate_queryset(users_list, page_number)

    context = {
        'participants': participants,
        'active_filter': active_filter,
        'filter_title': filter_title,
    }
    return render(request, 'users/participants.html', context)
