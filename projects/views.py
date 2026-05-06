"""
Представления для приложения projects.
Обрабатывают список проектов, создание, редактирование,
избранное и участие в проектах.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Project
from .forms import ProjectForm


def project_list_view(request):
    """
    Главная страница со списком проектов.
    Отображаются только открытые проекты, сортировка от новых к старым.
    Пагинация: 12 проектов.
    """
    projects_list = Project.objects.all().order_by('-created_at')
    paginator = Paginator(projects_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'projects/project_list.html', {'page_obj': page_obj})


def project_detail_view(request, project_id):
    """Страница детальной информации о проекте"""
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def create_project_view(request):
    """Создание нового проекта"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': False
    })


@login_required
def edit_project_view(request, project_id):
    """Редактирвоание проекта владельцем"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True
    })


@login_required
def complete_project_view(request, project_id):
    """Завершение проекта"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if project.status == 'open':
        project.status = 'closed'
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})

    return JsonResponse(
        {'status': 'error', 'message': 'Project cannot be completed'},
        status=400
    )


@login_required
def toggle_favorite_view(request, project_id):
    """Добавление/удаление проекта в избранное"""
    project = get_object_or_404(Project, id=project_id)

    if project in request.user.favorites.all():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True

    return JsonResponse({'status': 'ok', 'favorited': favorited})


@login_required
def toggle_participate_view(request, project_id):
    """Присоединение/выход из участников проекта"""
    project = get_object_or_404(Project, id=project_id)

    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_participant = False
    else:
        project.participants.add(request.user)
        is_participant = True

    return JsonResponse({
        'status': 'ok',
        'is_participant': is_participant,
        'participants_count': project.participants.count()
    })


@login_required
def favorite_projects_view(request):
    """Страница избранных проектов для авторизованных"""
    projects = request.user.favorites.all().order_by('-created_at')
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    return render(request, 'projects/favorite_projects.html', {'projects': projects})
