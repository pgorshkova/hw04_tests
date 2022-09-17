from django.db import models
from django.contrib.auth import get_user_model

LINE_NUMBER = 15

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name="Текст",
                            help_text='заполните это поле')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name="Группа",
        help_text='заполните это поле'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:LINE_NUMBER]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField('slug', unique=True, )
    description = models.TextField()

    def __str__(self):
        return self.title[:LINE_NUMBER]
