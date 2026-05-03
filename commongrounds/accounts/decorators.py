from functools import wraps

from django.shortcuts import redirect


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            profile = getattr(request.user, 'profile', None)
            if profile is None or profile.role != role:
                return redirect('accounts:permission-denied')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
