
from django.core.paginator import Paginator
from django.conf import settings


def paginate_queryset(queryset, request, page_size=None):
    """
    Универсальная функция для пагинации.

    Args:
        queryset: QuerySet для пагинации
        request: HTTP запрос
        page_size: Количество элементов на странице (по умолчанию из settings)

    Returns:
        Page объект с пагинированными данными
    """
    if page_size is None:
        page_size = getattr(settings, 'PAGE_SIZE', 12)

    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(request.GET.get('page'))
    return page_obj
