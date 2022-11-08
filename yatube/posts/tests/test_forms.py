# Каждый логический набор тестов — это класс,
# который наследуется от базового класса TestCase
from http import HTTPStatus

from django.test import TestCase, Client
from ..forms import PostForm
from django.contrib.auth import get_user_model
from ..models import Post, User, Group
from django.urls import reverse

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.group_1 = Group.objects.create(
            title='Тестовый заголовок Группы 1',
            description='текст группы 1',
            slug='test-slug'
        )
        # Создаем запись в базе данных
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test Post Text',
            group=cls.group_1
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test-group',
                                          description='Описание')

    def test_cant_create_existing_slug(self):
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        error_name1 = 'Данные поста не совпадают'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            text='Текст записанный в форму',
            group=self.group.id,
            author=self.user
        ).exists(), error_name1)
        error_name2 = 'Поcт не добавлен в базу данных'
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         error_name2)

    def test_can_edit_post(self):
        '''Проверка прав редактирования'''
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group_1)
        old_text = self.post
        self.group_2 = Group.objects.create(
            title='Тестовый заголовок Группы 2',
            description='текст группы 2',
            slug='test-slug-2'
        )

        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group_2.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name1 = 'Данные поста не совпадают'
        self.assertTrue(Post.objects.filter(
            group=self.group_2.id,
            author=self.user,
            pub_date=self.post.pub_date
        ).exists(), error_name1)
        error_name1 = 'Пользователь не может изменить содержание поста'
        self.assertNotEqual(old_text.text, form_data['text'], error_name1)
        error_name2 = 'Пользователь не может изменить группу поста'
        self.assertNotEqual(old_text.group, form_data['group'], error_name2)
        #
