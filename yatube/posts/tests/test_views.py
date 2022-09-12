from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
from django import forms

User = get_user_model()
POST_NUMBER = 10


class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="TestUser"
        )
        cls.random_user = User.objects.create_user(
            username="RandomUser"
        )
        cls.group = Group.objects.create(
            description="Тестовое описание",
            slug="Test-slug",
            title="Тестовое название"
        )
        cls.group_2 = Group.objects.create(
            description="Тестовое описание второй группы",
            slug="test-slug-group-2",
            title="Тестовое название второй группы"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="test test",
            group=cls.group
        )

    def setUp(self):
        self.client = Client()
        self.auth_client = Client()
        self.user = PostsViewsTest.user
        self.auth_client.force_login(self.user)
        self.post = PostsViewsTest.post

    def check_context_contains_page_or_post(self, context, post=False):
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, PostsViewsTest.user)
        self.assertEqual(post.pub_date, PostsViewsTest.post.pub_date)
        self.assertEqual(post.text, PostsViewsTest.post.text)
        self.assertEqual(post.group, PostsViewsTest.post.group)

    def test_view_funcs_correct_templates(self):
        names_templates = {
            reverse(
                "posts:index"
            ): "posts/index.html",
            reverse(
                "posts:post_create"
            ): "posts/create_post.html",
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.id}
            ): "posts/create_post.html",
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            ): "posts/profile.html",
        }
        for url, template in names_templates.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        response = self.auth_client.get(reverse("posts:index"))
        self.check_context_contains_page_or_post(response.context)

    def test_group_posts_correct_context(self):
        response = self.auth_client.get(
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            )
        )

        self.check_context_contains_page_or_post(response.context)
        self.assertIn('group', response.context)
        group = response.context['group']
        self.assertEqual(group.title, PostsViewsTest.group.title)
        self.assertEqual(group.description, PostsViewsTest.group.description)

    def test_post_detail_correct_context(self):
        response = self.auth_client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.id}
            )
        )
        self.check_context_contains_page_or_post(response.context, post=True)
        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'], PostsViewsTest.user)

    def test_edit_post_correct_context(self):
        """Test post edit page has correct context."""
        response = self.auth_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['post'].text,
                         'test test')
        self.assertEqual(response.context['post'].author.username,
                         'TestUser')
        self.assertEqual(response.context['post'].group.title,
                         'Тестовое название')

    def test_profile_use_correct_context(self):
        response = self.auth_client.get(
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            )
        )
        self.check_context_contains_page_or_post(response.context)

    def test_post_created_at_right_group_and_profile(self):
        urls = (
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group_2.slug}
            ),
            reverse(
                "posts:profile",
                kwargs={"username": self.random_user.username}
            )
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                page_obj = response.context.get("page_obj")

                self.assertEqual(len(page_obj), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="qwerty"
        )
        cls.group = Group.objects.create(
            description="Тестовое описание",
            slug="test-slug",
            title="Тестовое название"
        )
        posts = [
            Post(
                text=f'text {num}', author=cls.user,
                group=cls.group
            ) for num in range(1, 14)
        ]
        Post.objects.bulk_create(posts)

        cls.client = Client()

    def test_templates_paginator(self):
        urls = (
            reverse(
                "posts:index"
            ),
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            ),
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            ),
        )
        pages = [
            (1, POST_NUMBER),
            (2, Post.objects.count() - POST_NUMBER),
        ]
        for url in urls:
            with self.subTest(url=url):

                for page, expected_count in pages:
                    response = self.client.get(f"{url}?page={page}")
                    page_obj = response.context.get("page_obj")

                    self.assertEqual(
                        len(page_obj),
                        expected_count
                    )
