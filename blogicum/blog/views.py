"""View-функции приложения blog."""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from .forms import CommentForm, PostForm, RegistrationForm, UserEditForm
from .models import Category, Comment, Post

User = get_user_model()

POSTS_PER_PAGE = 10


def with_comment_count(queryset):
    """Добавляет к постам количество комментариев и сортирует их.

    Сортировка задаётся явно: в запросах с агрегацией (annotate)
    автоматическая сортировка из Meta.ordering не применяется.
    """
    return queryset.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def get_published_posts():
    """Возвращает опубликованные посты с опубликованной категорией.

    В выборку попадают только те публикации, у которых:
    - дата публикации не позже текущего момента;
    - флаг «опубликовано» установлен;
    - категория не снята с публикации.

    Текущее время вычисляется при каждом запросе, поэтому отложенные
    публикации становятся видимыми сразу после наступления их даты.
    """
    return with_comment_count(
        Post.objects.select_related(
            'author',
            'category',
            'location',
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    )


def paginate(request, queryset):
    """Возвращает страницу пагинации для переданного набора постов."""
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    return paginator.get_page(request.GET.get('page'))


def post_is_visible(post, user):
    """Проверяет, доступна ли публикация этому пользователю.

    Автор видит свои публикации всегда, остальным посетителям доступны
    только опубликованные посты с опубликованной категорией и датой
    публикации не позже текущего момента.
    """
    if user.is_authenticated and post.author_id == user.id:
        return True
    if not post.is_published:
        return False
    if post.category is None or not post.category.is_published:
        return False
    return post.pub_date <= timezone.now()


def index(request):
    """Отображает ленту публикаций с пагинацией."""
    return render(request, 'blog/index.html', {'page_obj': paginate(
        request, get_published_posts()
    )})


def category_posts(request, category_slug):
    """Отображает опубликованные публикации выбранной категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = with_comment_count(
        category.posts.select_related(
            'author',
            'category',
            'location',
        ).filter(
            is_published=True,
            pub_date__lte=timezone.now(),
        )
    )
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': paginate(request, post_list),
    })


def post_detail(request, post_id):
    """Отображает отдельную публикацию по её первичному ключу."""
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location'),
        pk=post_id,
    )
    if not post_is_visible(post, request.user):
        raise Http404('Публикация недоступна.')
    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': post.comments.select_related('author'),
        'form': CommentForm(),
    })


def profile(request, username):
    """Отображает страницу пользователя с его публикациями."""
    profile_user = get_object_or_404(User, username=username)
    post_list = profile_user.posts.select_related(
        'author',
        'category',
        'location',
    )
    if not (request.user.is_authenticated
            and request.user.id == profile_user.id):
        post_list = post_list.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': paginate(request, with_comment_count(post_list)),
    })


@login_required
def edit_profile(request):
    """Отображает и сохраняет форму редактирования профиля."""
    form = UserEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    """Создаёт новую публикацию от имени текущего пользователя."""
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Редактирует публикацию; доступно только её автору."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author_id != request.user.id:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    """Удаляет публикацию; доступно только её автору."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author_id != request.user.id:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', {'form': PostForm(
        instance=post
    )})


@login_required
def add_comment(request, post_id):
    """Добавляет комментарий к публикации."""
    post = get_object_or_404(Post, pk=post_id)
    if not post_is_visible(post, request.user):
        raise Http404('Публикация недоступна.')
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирует комментарий; доступно только его автору."""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author_id != request.user.id:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаляет комментарий; доступно только его автору."""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author_id != request.user.id:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})


class RegisterView(CreateView):
    """Страница регистрации нового пользователя."""

    form_class = RegistrationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
