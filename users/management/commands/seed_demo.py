"""Команда наполнения базы тестовыми данными.

Создаёт суперпользователя, нескольких обычных пользователей
(у каждого есть минимум один проект), участия и избранное.

Запуск: python manage.py seed_demo
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Project

User = get_user_model()

DEFAULT_PASSWORD = "TeamFinder123"

USERS = [
    {
        "email": "anna@example.com",
        "name": "Анна",
        "surname": "Иванова",
        "phone": "+79150000001",
        "about": "Backend-разработчик на Python. Люблю Django и чистый код.",
        "github_url": "https://github.com/anna-ivanova",
    },
    {
        "email": "boris@example.com",
        "name": "Борис",
        "surname": "Петров",
        "phone": "+79150000002",
        "about": "Frontend-разработчик. React, TypeScript, анимации.",
        "github_url": "https://github.com/boris-petrov",
    },
    {
        "email": "vera@example.com",
        "name": "Вера",
        "surname": "Сидорова",
        "phone": "+79150000003",
        "about": "UX/UI дизайнер. Помогу сделать интерфейс удобным.",
        "github_url": "https://github.com/vera-sidorova",
    },
    {
        "email": "grigory@example.com",
        "name": "Григорий",
        "surname": "Кузнецов",
        "phone": "+79150000004",
        "about": "DevOps-инженер. Docker, CI/CD, облака.",
        "github_url": "https://github.com/grigory-kuznetsov",
    },
    {
        "email": "daria@example.com",
        "name": "Дарья",
        "surname": "Смирнова",
        "phone": "+79150000005",
        "about": "Аналитик данных, изучаю ML. Ищу команду для pet-проектов.",
        "github_url": "https://github.com/daria-smirnova",
    },
]

PROJECTS = [
    {
        "owner": "anna@example.com",
        "name": "Сервис обмена книгами",
        "description": (
            "Платформа, где можно обмениваться бумажными книгами с людьми "
            "из своего города. Нужны frontend-разработчик и дизайнер."
        ),
        "status": "open",
        "github_url": "https://github.com/anna-ivanova/book-exchange",
    },
    {
        "owner": "anna@example.com",
        "name": "Трекер привычек",
        "description": (
            "Мобильное веб-приложение для отслеживания полезных привычек "
            "с напоминаниями и статистикой."
        ),
        "status": "closed",
        "github_url": "",
    },
    {
        "owner": "boris@example.com",
        "name": "Карта кофеен",
        "description": (
            "Интерактивная карта лучших кофеен города с отзывами "
            "и рейтингами. Ищу backend-разработчика."
        ),
        "status": "open",
        "github_url": "https://github.com/boris-petrov/coffee-map",
    },
    {
        "owner": "vera@example.com",
        "name": "Конструктор резюме",
        "description": (
            "Онлайн-конструктор красивых резюме с экспортом в PDF. "
            "Дизайн готов, нужна помощь с реализацией."
        ),
        "status": "open",
        "github_url": "",
    },
    {
        "owner": "grigory@example.com",
        "name": "Мониторинг домашнего сервера",
        "description": (
            "Лёгкая панель мониторинга для домашних серверов и Raspberry Pi: "
            "метрики, алерты, телеграм-бот."
        ),
        "status": "open",
        "github_url": "https://github.com/grigory-kuznetsov/home-monitor",
    },
    {
        "owner": "daria@example.com",
        "name": "Рекомендатель фильмов",
        "description": (
            "Сервис рекомендаций фильмов на основе истории просмотров. "
            "Нужны разработчики, интересующиеся ML."
        ),
        "status": "open",
        "github_url": "",
    },
]

PARTICIPATIONS = {
    "Сервис обмена книгами": ["boris@example.com", "vera@example.com"],
    "Карта кофеен": ["anna@example.com", "daria@example.com"],
    "Конструктор резюме": ["boris@example.com"],
    "Рекомендатель фильмов": ["grigory@example.com", "anna@example.com"],
}

FAVORITES = {
    "anna@example.com": ["Карта кофеен", "Рекомендатель фильмов"],
    "boris@example.com": ["Сервис обмена книгами"],
    "vera@example.com": ["Сервис обмена книгами", "Мониторинг домашнего сервера"],
    "daria@example.com": ["Конструктор резюме"],
}


class Command(BaseCommand):
    help = "Наполняет базу тестовыми пользователями и проектами."

    def handle(self, *args, **options):
        if not User.objects.filter(email="admin@example.com").exists():
            User.objects.create_superuser(
                email="admin@example.com",
                password=DEFAULT_PASSWORD,
                name="Админ",
                surname="Админов",
            )
            self.stdout.write(self.style.SUCCESS(
                "Суперпользователь admin@example.com создан."
            ))

        users = {}
        for data in USERS:
            user = User.objects.filter(email=data["email"]).first()
            if user is None:
                user = User.objects.create_user(
                    password=DEFAULT_PASSWORD, **data
                )
                self.stdout.write(f"Пользователь {user.email} создан.")
            users[user.email] = user

        projects = {}
        for data in PROJECTS:
            owner = users[data.pop("owner")]
            project = Project.objects.filter(
                name=data["name"], owner=owner
            ).first()
            if project is None:
                project = Project.objects.create(owner=owner, **data)
                project.participants.add(owner)
                self.stdout.write(f"Проект «{project.name}» создан.")
            data["owner"] = owner.email
            projects[project.name] = project

        for project_name, emails in PARTICIPATIONS.items():
            for email in emails:
                projects[project_name].participants.add(users[email])

        for email, project_names in FAVORITES.items():
            for project_name in project_names:
                users[email].favorites.add(projects[project_name])

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Пароль всех тестовых пользователей: {DEFAULT_PASSWORD}"
        ))
