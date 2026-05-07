from django.shortcuts import redirect
from functools import wraps

def verification_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 1. Если не вошел — на логин
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        # 2. Если вошел, но не подтвердил телефон — на страницу ввода кода
        if not getattr(request.user, 'is_verified', False):
            return redirect('users:verify_phone')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view