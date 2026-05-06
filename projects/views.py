"""
Представления для приложения projects.
Обрабатывают список проектов, создание, редактирование,
избранное и участие в проектах.
"""

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from constants import PAGINATION_PAGE_SIZE

from .forms import ProjectForm
from .models import Project


def project_list_view(request):
    """
    Главная страница со списком проектов.
    """
    projects_list = (
        Project.objects
        .select_related('owner')
        .prefetch_related('participants')
    )
    paginator = Paginator(projects_list, PAGINATION_PAGE_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'projects/project_list.html', {'page_obj': page_obj})


def project_detail_view(request, project_id):
    """Страница детальной информации о проекте"""
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related('participants'),
        id=project_id
    )
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def create_project_view(request):
    """Создание нового проекта"""
    if request.method != 'POST':
        form = ProjectForm()
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': False
        })

    form = ProjectForm(request.POST)
    if not form.is_valid():
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': False
        })

    project = form.save(commit=False)
    project.owner = request.user
    project.save()
    project.participants.add(request.user)
    return redirect('projects:project_detail', project_id=project.id)


@login_required
def edit_project_view(request, project_id):
    """Редактирование проекта владельцем"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method != 'POST':
        form = ProjectForm(instance=project)
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': True
        })

    form = ProjectForm(request.POST, instance=project)
    if not form.is_valid():
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': True
        })

    form.save()
    return redirect('projects:project_detail', project_id=project.id)


@login_required
def complete_project_view(request, project_id):
    """Завершение проекта"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if project.status == Project.Status.OPEN:
        project.status = Project.Status.CLOSED
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
    projects = (
        request.user.favorites
        .select_related('owner')
        .prefetch_related('participants')
    )
    paginator = Paginator(projects, PAGINATION_PAGE_SIZE)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    return render(request, 'projects/favorite_projects.html', {'projects': projects})
