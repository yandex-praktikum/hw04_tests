from django.core.paginator import Paginator

from yatube.settings import COUNT_POSTS


def main_paginator(post_list, request):
    """Функция позволяет выводить текст и другое содержимое
    в заданном количестве на отдельные страницы, к которым она применена.
    """
    paginator = Paginator(post_list, COUNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return context
