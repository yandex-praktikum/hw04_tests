from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='karelin')
        cls.group = Group.objects.create(
            title='Группа',
            slug='my_slug',
            description='Группа',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст тестового поста',
            group=cls.group
        )

    def test_post_model_have_correct_object_names(self):
        post = self.post
        expected_name = post.text[:15]
        self.assertEqual(expected_name, str(post))

    def test_group_model_have_correct_object_names(self):
        group = self.group
        expected_name = group.title
        self.assertEqual(expected_name, str(group))
