from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUserNoName1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст не самого длинного поста, больше 15 символов',
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': "Текст",
            'group': 'Группа',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(str(post), expected_object_name)

    def test_group_has_correct_str_name(self):
        group = self.group
        expected_object_name = group.title[:15]
        self.assertEqual(str(group), expected_object_name)

    def test_help_text(self):
        """Test correct help texts of model's fields."""
        post = self.post
        field_help = {
            'text': 'заполните это поле',
            'group': 'заполните это поле',
        }
        for value, expected in field_help.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)