"""Настройка админ-зоны приложения blog."""
from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админ-класс публикаций."""

    list_display = (
        'title',
        'author',
        'category',
        'location',
        'pub_date',
        'is_published',
    )
    list_editable = ('is_published',)
    list_filter = ('is_published', 'category', 'location')
    search_fields = ('title', 'text')
    list_select_related = ('author', 'category', 'location')
    date_hierarchy = 'pub_date'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ-класс категорий."""

    list_display = ('title', 'slug', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('title', 'description')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Админ-класс местоположений."""

    list_display = ('name', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админ-класс комментариев."""

    list_display = ('post', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text',)
    list_select_related = ('post', 'author')
