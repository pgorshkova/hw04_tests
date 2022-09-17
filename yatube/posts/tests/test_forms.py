from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase
from http import HTTPStatus

from posts.models import Post, Group


User = get_user_model()


class PostFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Test_User'
        )
        cls.post_to_be_changed = Post.objects.create(
            text='Тестовый текст, надо изменить',
            author=cls.user
        )
        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test_slug',
                                         description='Тестовое описание')

    def setUp(self) -> None:
        self.guest_client = Client()
        self.logged_client = Client()
        self.logged_client.force_login(self.user)

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
        response = self.logged_client.post(
            reverse('posts:profile',
                    kwargs={
                        'username': PostFormTest.user.username
                    }),
            data={
                'text': 'Test post',
                'group': PostFormTest.group.id
            },
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_data = {
            'text': 'Test post',
            'group': PostFormTest.group.id,
            'author': PostFormTest.user
        }
        response = self.logged_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={
                    'username': PostFormTest.user.username
                }
            )
        )
        post = Post.objects.first()
        self.assertEqual(post.text, 'Test post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, PostFormTest.group)
        self.assertEqual(Post.objects.count(), 2)

    def test_edit_post_changed_with_same_id(self):
        post_id = self.post_to_be_changed.pk
        changed_data = {
            'text': 'Изменённый текстовый текст'
        }
        self.logged_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=changed_data
        )
        self.assertEqual(Post.objects.get(pk=post_id).text,
                         'Изменённый текстовый текст')

    def test_guest_user_create_post(self):
        form_data = {
            'text': 'guest edit post',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/create/')
        )
        self.assertEqual(Post.objects.count(), 1)
