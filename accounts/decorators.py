from django.shortcuts import redirect


def redirect_if_authenticated(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main:dashboard')
        return func(request, *args, **kwargs)

    return wrapper
