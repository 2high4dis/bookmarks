from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm


@login_required
def dashboard(request: HttpRequest):
    template_name = 'account/dashboard.html'
    return render(request=request, template_name=template_name, context={'section': 'dashboard'})


def register(request: HttpRequest):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request=request, template_name='account/register_done.html', context={'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request=request, template_name='account/register.html', context={'user_form': user_form})
