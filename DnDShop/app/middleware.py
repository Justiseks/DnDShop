# app/middleware.py
from django.shortcuts import redirect

class AdminAccessRestrictionMiddleware:
    """
    Перенаправляет всех (анонимов, клиентов, менеджеров и т.д.)
    с любого URL начинающегося на /admin/ на главную страницу,
    если пользователь не является superuser.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or ''
        # если путь начинается с /admin/ и пользователь не суперюзер — редирект на home
        if path.startswith('/admin/') and not (hasattr(request, 'user') and request.user.is_superuser):
            return redirect('home')
        return self.get_response(request)