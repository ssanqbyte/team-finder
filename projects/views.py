from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project


def project_list(request):
    """Главная страница: все проекты от новых к старым с пагинацией."""
    projects = Project.objects.select_related("owner").order_by("-created_at")
    paginator = Paginator(projects, settings.PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {"projects": page_obj, "page_obj": page_obj, "extra_query": ""}
    return render(request, "projects/project_list.html", context)


@login_required
def favorite_projects(request):
    """Страница избранных проектов текущего пользователя."""
    projects = (
        request.user.favorites.select_related("owner").order_by("-created_at")
    )
    return render(
        request, "projects/favorite_projects.html", {"projects": projects}
    )


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
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", project_id=project.id)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project(request, project_id):
    """Редактирование существующего проекта (только автор)."""
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return HttpResponseForbidden("Редактировать проект может только автор.")
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("projects:detail", project_id=project.id)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@require_POST
def complete_project(request, project_id):
    """Завершение проекта автором: смена статуса open -> closed."""
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error"}, status=403)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user or project.status != "open":
        return JsonResponse({"status": "error"}, status=403)
    project.status = "closed"
    project.save()
    return JsonResponse({"status": "ok", "project_status": "closed"})


@require_POST
def toggle_favorite(request, project_id):
    """Добавление/удаление проекта в избранном текущего пользователя."""
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error"}, status=403)
    project = get_object_or_404(Project, pk=project_id)
    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@require_POST
def toggle_participate(request, project_id):
    """Присоединение к проекту / отказ от участия."""
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error"}, status=403)
    project = get_object_or_404(Project, pk=project_id)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})
