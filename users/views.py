from django.conf import settings
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, ProfileEditForm, RegisterForm

User = get_user_model()

USER_FILTERS = (
    "owners-of-favorite-projects",
    "owners-of-participating-projects",
    "interested-in-my-projects",
    "participants-of-my-projects",
)


def register_view(request):
    """Регистрация нового пользователя."""
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """Вход в систему по email и паролю."""
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            login(request, user)
            return redirect("projects:list")
        form.add_error(None, "Неверный email или пароль")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    """Выход из аккаунта."""
    logout(request)
    return redirect("projects:list")


def users_list(request):
    """Список пользователей с фильтрацией (вариант 1) и пагинацией."""
    participants = User.objects.order_by("-id")
    active_filter = request.GET.get("filter")
    if not (request.user.is_authenticated and active_filter in USER_FILTERS):
        active_filter = None

    if active_filter == "owners-of-favorite-projects":
        participants = participants.filter(
            owned_projects__in=request.user.favorites.all()
        ).distinct()
    elif active_filter == "owners-of-participating-projects":
        participants = participants.filter(
            owned_projects__participants=request.user
        ).distinct()
    elif active_filter == "interested-in-my-projects":
        participants = participants.filter(
            favorites__owner=request.user
        ).distinct()
    elif active_filter == "participants-of-my-projects":
        participants = participants.filter(
            participated_projects__owner=request.user
        ).distinct()

    paginator = Paginator(participants, settings.PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "participants": page_obj,
        "active_filter": active_filter,
        "page_obj": page_obj,
        "extra_query": f"filter={active_filter}" if active_filter else "",
    }
    return render(request, "users/participants.html", context)


def user_detail(request, user_id):
    """Публичный профиль пользователя."""
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    """Редактирование собственного профиля."""
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:detail", user_id=request.user.id)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    """Смена пароля залогиненного пользователя."""
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", user_id=user.id)
    return render(request, "users/change_password.html", {"form": form})
