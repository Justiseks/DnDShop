# app/utils.py
from functools import wraps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse

def _in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()

def is_client(user):
    return _in_group(user, 'Client')

def is_manager(user):
    return _in_group(user, 'Manager')

def client_required(view_func):
    """Если не аутентифицирован — редирект на логин; если аутентифицирован, но не Client — редирект на главную."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        login_url = reverse('login')
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url=login_url, redirect_field_name=REDIRECT_FIELD_NAME)
        if not is_client(request.user):
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def manager_required(view_func):
    """Если не аутентифицирован — редирект на логин; если аутентифицирован, но не Manager — редирект на главную."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        login_url = reverse('login')
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url=login_url, redirect_field_name=REDIRECT_FIELD_NAME)
        if not is_manager(request.user):
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
