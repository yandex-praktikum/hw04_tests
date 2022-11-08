from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        # Получаю значение поля
        self.assertEqual(
            group.__str__(),
            'Тестовая группа',
            f'Ошибка в методе {group.__str__.__name__} модели group'
        )
        post = PostModelTest.post
        self.assertEqual(
            post.__str__(),
            post.text[:15],
            f'Ошибка в методе {post.__str__.__name__} модели post'
        )
