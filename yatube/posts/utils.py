from django.core.paginator import Paginator

from yatube.settings import PAGE_SIZE


def main_paginator(post_list, request):
    paginator = Paginator(post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return context
