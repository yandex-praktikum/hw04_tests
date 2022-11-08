from django.test import TestCase, Client
from ..models import Group, Post
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskURLTests(TestCase):
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
            text='Test Post',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # это уже другой пользователь с именем HasNoName
        """self.user1 = User.objects.create_user(username='HasNoName')"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # 1) Проверить страницы для авторизированнного и не авторизированнного пользователя
    # 2) Проверить страницу Create на редирект

    # Проверка Urls на статус 200
    def test_home_page(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_slug_url_exists_at_desired_location_authorized(self):
        """Страница /group/slug/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location_authorized(self):
        """Страница /profile/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get(f'/profile/{self.user}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location_authorized(self):
        """Страница /profile/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_post_id_url_exists_at_desired_location_authorized(self):
        """Страница /post/id/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /task/test_slug/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_post_id_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /post/post_id/edit перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit',
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/edit/',
            status_code=301

        )

    # Проверка шаблонов
    def test_home_url_uses_correct_template(self):
        """Страница по адресу / использует шаблон deals/home.html."""
        response = self.authorized_client.get('/')
        self.assertTemplateUsed(response, 'posts/index.html')

    def test_group_slug_url_uses_correct_template(self):
        """Страница по адресу /group/{self.group.slug}/
         использует шаблон 'posts/group_list.html'."""
        response = self.authorized_client.get(f'/group/{self.group.slug}/')
        self.assertTemplateUsed(response, 'posts/group_list.html')

    def test_profile_url_uses_correct_template(self):
        """Страница по адресу /profile/{self.user}/
         использует шаблон 'posts/profile.html'."""
        response = self.authorized_client.get(f'/profile/{self.user}/')
        self.assertTemplateUsed(response, 'posts/profile.html')

    def test_post_id_url_uses_correct_template(self):
        """Страница по адресу /profile/{self.user}/
         использует шаблон 'posts/profile.html'."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/')
        self.assertTemplateUsed(response, 'posts/post_detail.html')
