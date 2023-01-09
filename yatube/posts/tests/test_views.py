from collections import namedtuple

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Page
from django.test import TestCase, Client
from django.urls import reverse

from . .forms import PostForm
from . .models import Group, Post

User = get_user_model()


class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='karelin')
        cls.group = Group.objects.create(
            title='Группа',
            slug='my_slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст тестового поста',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        '''Функция использует правильный шаблон.'''

        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}):
                    'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}):
                    'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}):
                    'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}):
                    'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон главной страницы сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        context = response.context.get('page_obj')[0]
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.pub_date, self.post.pub_date)
        self.assertEqual(context.author, self.user)
        self.assertEqual(context.group, self.group)

    def test_group_list_page_show_correct_context(self):
        """Шаблон страницы группы сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug})
        )
        context = response.context.get('page_obj')[0]
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.pub_date, self.post.pub_date)
        self.assertEqual(context.author, self.user)
        self.assertEqual(context.group, self.group)
        context_group = response.context.get('group')
        self.assertEqual(context_group, self.group)

    def test_post_not_appears_at_wrong_group(self):
        """Пост не появляется в другой группе."""
        group_2 = Group.objects.create(
            title='Другая группа',
            slug='slug_2'
        )
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост с неправильной группой',
            group=group_2,
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': group_2.slug})
        )
        self.assertEqual(len(response.context.get('page_obj')), 1)
        context_post = response.context.get('page_obj')
        self.assertIn(post, context_post)
        self.assertNotIn(self.post, context_post)

    def test_profile_page_show_correct_context(self):
        """Шаблон страницы автора сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                kwargs={'username': self.user.username}))
        context = response.context.get('page_obj')[0]
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.pub_date, self.post.pub_date)
        self.assertEqual(context.author, self.user)
        self.assertEqual(context.group, self.group)
        context_author = response.context.get('author')
        self.assertEqual(context_author, self.post.author)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон страницы поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        ))
        context = response.context.get('post')
        self.assertIsInstance(context, Post)
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.pub_date, self.post.pub_date)
        self.assertEqual(context.author, self.user)
        self.assertEqual(context.group, self.group)

    def test_post_create_page_show_correct_context(self):
        """Шаблон страницы создания нового поста сформирован
        с правильным контекстом.
        """
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                context_form_field = response.context.get('form').fields[value]
                self.assertIsInstance(context_form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон страницы редактирования поста сформирован
        с правильным контекстом.
        """
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        ))
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertTrue(response.context.get('is_edit'))
        context = response.context.get('post')
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.pub_date, self.post.pub_date)
        self.assertEqual(context.author, self.user)
        self.assertEqual(context.group, self.group)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                context_form_field = response.context.get('form').fields[value]
                self.assertIsInstance(context_form_field, expected)

class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text='Текст тестового поста ' + str(i),
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.client = Client()

    def test_paginator_posts_per_page(self):
        first_page_posts_count = 10
        second_page_posts_count = 3
        context = {
            reverse('posts:index'): first_page_posts_count,
            reverse('posts:index') + '?page=2': second_page_posts_count,
            reverse('posts:group_list', kwargs={'slug': self.group.slug, }):
            first_page_posts_count,
            reverse('posts:group_list', kwargs={'slug': self.group.slug, })
            + '?page=2': second_page_posts_count,
            reverse('posts:profile', kwargs={'username': self.user.username}):
            first_page_posts_count,
            reverse('posts:profile', kwargs={'username': self.user.username})
            + '?page=2': second_page_posts_count,
        }
        for reverse_page, posts_count in context.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.client.get(reverse_page)
                self.assertEqual(len(response.context.get('page_obj')),
                                 posts_count)
