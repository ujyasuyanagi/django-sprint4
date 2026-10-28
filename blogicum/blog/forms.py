"""Формы приложения blog."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма создания и редактирования публикации."""

    pub_date = forms.DateTimeField(
        label='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
        input_formats=(
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
        ),
    )

    class Meta:
        """Настройки формы публикации."""

        model = Post
        exclude = ('author',)


class CommentForm(forms.ModelForm):
    """Форма создания и редактирования комментария."""

    class Meta:
        """Настройки формы комментария."""

        model = Comment
        fields = ('text',)


class UserEditForm(forms.ModelForm):
    """Форма редактирования профиля пользователя."""

    class Meta:
        """Настройки формы профиля."""

        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class RegistrationForm(UserCreationForm):
    """Форма регистрации нового пользователя."""

    class Meta(UserCreationForm.Meta):
        """Настройки формы регистрации."""

        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
