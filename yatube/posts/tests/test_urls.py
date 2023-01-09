from http import HTTPStatus
from operator import itemgetter

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_author = User.objects.create_user(username='karelin')
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Текст тестового поста',
        )
        cls.group = Group.objects.create(
            title='Группа',
            slug='my_slug'
        )
        cls.urls = {
            'index': ('/', 'posts/index.html',),
            'group': (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            'profile': (
                f'/profile/{cls.user.username}/',
                'posts/profile.html',
            ),
            'post': (f'/posts/{cls.post.pk}/', 'posts/post_detail.html',),
            'create': ('/create/', 'posts/create_post.html',),
            'edit': (f'/posts/{cls.post.pk}/edit/', 'posts/create_post.html',)
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.user_author)

    def test_posts_urls_exists_at_desired_locations(self):
        '''Станицы существуют по заданным адресам.'''
        urls = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
            '/create/',
            f'/posts/{self.post.pk}/edit/'
        )
        for url in urls:
            with self.subTest():
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_ulrs_available_for_anonimus(self):
        '''Станицы доступны для анонимного пользователя.'''
        urls = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
        )
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_redirect_anonymous(self):
        '''Страницы переадресуют анонимного пользователя.'''
        urls = (
            '/create/',
            f'/posts/{self.post.pk}/edit/'
        )
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_posts_edit_redirect_not_author(self):
        '''Переадресация не автора со страницы редактирования поста .'''
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/', follow=True)
        self.assertRedirects(response, f'/posts/{self.post.pk}/')    

    def test_posts_urls_uses_correct_templates(self):
        '''Страницы используют правильные шаблоны.'''
        templates_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html'
        }
        for url, template in templates_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        '''запрос к несуществующей странице вернёт ошибку 404'''
        response = self.guest_client.get('/whatever/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
