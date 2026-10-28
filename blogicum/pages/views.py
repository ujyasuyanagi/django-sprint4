"""View-классы и обработчики ошибок приложения pages."""
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Страница «О проекте»."""

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Страница «Наши правила»."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Отображает страницу ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Отображает страницу ошибки 403 (проблема с CSRF-токеном)."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Отображает страницу ошибки 500."""
    return render(request, 'pages/500.html', status=500)
