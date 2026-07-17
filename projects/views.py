# projects/views.py

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from http import HTTPStatus

from core.services import paginate_queryset
from .forms import ProjectForm
from .models import Project


def project_list(request):
    """Главная страница: все проекты от новых к старым с пагинацией."""
    projects = (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    page_obj = paginate_queryset(projects, request)
    return render(request, "projects/project_list.html", {"page_obj": page_obj})


@login_required
def favorite_projects(request):
    """Страница избранных проектов текущего пользователя."""
    projects = (
        request.user.favorites
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    page_obj = paginate_queryset(projects, request)
    return render(request, "projects/favorite_projects.html", {"page_obj": page_obj})


def project_detail(request, project_id):
    """Страница проекта."""
    project = get_object_or_404(
        Project.objects.select_related("owner"), pk=project_id
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    """Создание нового проекта."""
    form = ProjectForm(request.POST or None)
    if form.is_valid():  
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        return redirect("projects:project_detail", project_id=project.id)
    return render(request, "projects/create-project.html", {"form": form})


@login_required
def edit_project(request, project_id):
    """Редактирование существующего проекта (только автор)."""
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return HttpResponseRedirect("Редактировать проект может только автор.")
    
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():  
        form.save()
        return redirect("projects:project_detail", project_id=project.id)
    
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@require_POST
def complete_project(request, project_id):
    """Завершение проекта автором: смена статуса open -> closed."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "Authentication required"},
            status=HTTPStatus.UNAUTHORIZED
        )
    
    project = get_object_or_404(Project, pk=project_id)
    
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Only owner can complete project"},
            status=HTTPStatus.FORBIDDEN
        )
    
    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Project is already completed"},
            status=HTTPStatus.BAD_REQUEST
        )
    
    project.status = Project.STATUS_CLOSED 
    project.save()
    
    return JsonResponse({
        "status": "ok",
        "project_status": Project.STATUS_CLOSED  
    })


@require_POST
def toggle_favorite(request, project_id):
    """Добавление/удаление проекта в избранном текущего пользователя."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "Authentication required"},
            status=HTTPStatus.UNAUTHORIZED
        )
    
    project = get_object_or_404(Project, pk=project_id)
    
    if (is_favorited := request.user.favorites.filter(pk=project.pk).exists()):
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    
    return JsonResponse({
        "status": "ok",
        "favorited": is_favorited
    })


@require_POST
def toggle_participate(request, project_id):
    """Присоединение к проекту / отказ от участия."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "Authentication required"},
            status=HTTPStatus.UNAUTHORIZED
        )
    
    project = get_object_or_404(Project, pk=project_id)
    
    if (is_participant := project.participants.filter(pk=request.user.pk).exists()):
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    
    return JsonResponse({
        "status": "ok",
        "participant": is_participant
    })