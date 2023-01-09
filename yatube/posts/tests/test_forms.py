from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from . .models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='karelin')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='my_slug',
            description='Группа'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.order_by('pub_date').last()
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)

    def test_edit_post(self):
        """Валидная форма редактирует запись."""
        post = Post.objects.create(
            text='Пост для редактирования',
            group=self.group,
            author=self.user
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный пост',
            'group': post.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.pk}
            ),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=post.pk)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.pk}
        ))
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(Post.objects.count(), posts_count)
