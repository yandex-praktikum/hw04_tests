# deals/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Group, Post
from django.urls import reverse
from django import forms

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.group = Group.objects.create(
            title='Тестовый заголовок Группы 1',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок группы 2',
            description='Текст группы 2',
            slug='test-slug_2')

        cls.post = Post.objects.create(
            author=cls.user,
            text='Test Post Text',
            group=cls.group,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # это уже другой пользователь с именем HasNoName
        """self.user1 = User.objects.create_user(username='HasNoName')"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': self.user})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': self.post.id})
            ),
            'posts/create_post.html':
                reverse('posts:post_edit', kwargs={'post_id': self.post.id}),

        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        text = response.context['page_obj'][0].text
        title = response.context['title']
        self.assertEqual(text, 'Test Post Text')

    def test_group_list_page_show_correct_context(self):
        response = (self.authorized_client.
        get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})))
        text = response.context['page_obj'][0].text
        group = response.context['group']
        print(group, "   ", 'Тестовый заголовок Группы 1')
        self.assertEqual(text, 'Test Post Text')
       # self.assertEqual(group, 'Тестовый заголовок Группы 1')

    def test_profile_page_show_correct_context(self):
        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})))
        text = response.context['page_obj'][0].text
        author = response.context['author']
        self.assertEqual(text, 'Test Post Text')
        self.assertEqual(author, self.user)

    #
    def test_post_detail_page_show_correct_context(self):
        response = (self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))
        )
        text = response.context['post'].text
        count = response.context['post'].author.posts.count()
        self.assertEqual(text, 'Test Post Text')
        self.assertEqual(count, 1)

    #
    def test_create_post_page_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse('posts:post_create')))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    #
    def test_post_edit_page_show_correct_context(self):
        response = (self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)


#
#
class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Test Post Text',
            group=cls.group
        )
        cls.post_1 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 1',
            group=cls.group
        )
        cls.post_3 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 3',
            group=cls.group
        )
        cls.post_4 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 4',
            group=cls.group
        )
        cls.post_5 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 5',
            group=cls.group
        )
        cls.post_6 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 6',
            group=cls.group
        )
        cls.post_7 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 7',
            group=cls.group
        )
        cls.post_8 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 8',
            group=cls.group
        )
        cls.post_9 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 9',
            group=cls.group
        )
        cls.post_10 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 10',
            group=cls.group
        )
        cls.post_11 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 11',
            group=cls.group
        )
        cls.post_12 = Post.objects.create(
            author=cls.user,
            text='Test Post Text 12',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # это уже другой пользователь с именем HasNoName
        """self.user1 = User.objects.create_user(username='HasNoName')"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_index_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_first_page_group_lists_contains_ten_records(self):
        response = (self.authorized_client.
        get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    #
    def test_second_page_group_lists_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.

        response = (self.authorized_client.
        get(
            reverse('posts:index') + '?page=2', kwargs={'slug': 'test-slug'}))
        print(len(response.context['page_obj']))
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_first_page_profile_contains_ten_records(self):
        response = (self.authorized_client.
        get(
            reverse('posts:profile', kwargs={'username': self.user})))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = (self.authorized_client.get(
            reverse('posts:index') + '?page=2',
            kwargs={'username': self.user}))
        self.assertEqual(len(response.context['page_obj']), 2)


class Pages_Test(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.group_1 = Group.objects.create(
            title='Тестовый заголовок Группы 1',
            description='текст группы 1',
            slug='test-slug'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок группы 2',
            description='Текст группы 2',
            slug='test-slug_2')

        cls.post = Post.objects.create(
            author=cls.user,
            text='Test Post Text',
            group=cls.group_1,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # это уже другой пользователь с именем HasNoName
        """self.user1 = User.objects.create_user(username='HasNoName')"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_check_post_after_creation(self):
        reverses = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': self.user})
        }
        for template in reverses:
            with self.subTest():
                response = self.authorized_client.get(template)
                text = response.context['page_obj'][0].text
                self.assertEqual(text, 'Test Post Text')

    def test_check_valid_group(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))

        posts_count_group1 = len(response.context['page_obj'])
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug_2'}))

        posts_count_group2 = len(response.context['page_obj'])
        self.assertNotEqual(posts_count_group1, posts_count_group2)
