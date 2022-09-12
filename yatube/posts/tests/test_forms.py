from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase

from posts.models import Post


User = get_user_model()


class PostFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Test_User'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )
        cls.post_to_be_changed = Post.objects.create(
            text='Тестовый текст, надо изменить',
            author=cls.user
        )

    def setUp(self) -> None:
        self.logged_client = Client()
        self.logged_client.force_login(self.user)

    def test_post_appears_in_db(self):
        """Test new post appears in database and redirects after success."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст 1',
            'author': self.user.username
        }
        response = self.logged_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post_changed_with_same_id(self):
        """Test that post has the same pk after been edited."""
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
