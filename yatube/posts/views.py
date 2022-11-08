# posts/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from .utils import page_paginator


def index(request):
    post_list = Post.objects.all()
    title = "Последние обновления на сайте"
    page_obj = page_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    # Получаю объект класса групп
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    page_obj = page_paginator(request, posts)
    title = f"Последние {posts.count()} поста группы {slug}"
    context = {
        'page_obj': page_obj,
        'group': group,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    # Не совсем понял про related_name ведь его нет в модели Post
    # и что именно нужно передать в него
    name = author.get_full_name()
    title = f"Профайл пользователя {name}"
    context = {
        'page_obj': page_paginator(request, post_list),
        'title': title,
        'author': author,
        'count': post_list.count(),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    # Здесь код запроса к модели и создание словаря контекста
    post = get_object_or_404(Post, id=post_id)
    total_author_posts = post.author.posts.count()
    context = {
        'post': post,
        'total_posts': total_author_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    username = request.user.username
    form = PostForm()
    context = {
        'title': 'Новый пост',
        'form': form,
    }
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=username)
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    # Хотелось бы прочитать про вот этот вид записи,
    # подскажите как он называется?
    context = {
        'title': 'Редактировать пост',
        'form': form,
        'is_edit': True,
    }
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        # Убрал строку так как не совсем понимаю зачем она вообще нужна была
    return render(request, "posts/create_post.html", context)
