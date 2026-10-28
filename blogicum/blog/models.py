"""Модели приложения blog."""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PublishedBaseModel(models.Model):
    """Абстрактная модель с общими полями публикуемых объектов."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        """Настройки абстрактной модели."""

        abstract = True


class Category(PublishedBaseModel):
    """Тематическая категория, объединяющая публикации."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        ),
    )

    class Meta:
        """Сортировка и названия модели в обоих числах."""

        ordering = ('title',)
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Возвращает заголовок категории."""
        return self.title


class Location(PublishedBaseModel):
    """Географическая метка, к которой относится публикация."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название места',
    )

    class Meta:
        """Сортировка и названия модели в обоих числах."""

        ordering = ('name',)
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        """Возвращает название местоположения."""
        return self.name


class Post(PublishedBaseModel):
    """Публикация в блоге."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория',
    )
    image = models.ImageField(
        upload_to='posts_images',
        blank=True,
        null=True,
        verbose_name='Изображение',
    )

    class Meta:
        """Сортировка и названия модели в обоих числах."""

        ordering = ('-pub_date',)
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        """Возвращает заголовок публикации."""
        return self.title


class Comment(models.Model):
    """Комментарий к публикации."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        """Сортировка и названия модели в обоих числах."""

        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        """Возвращает первые символы текста комментария."""
        return self.text[:50]
