from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact


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

            Profile.objects.create(user=new_user)

            return render(request=request, template_name='account/register_done.html', context={'new_user': new_user})
    else:
        user_form = UserRegistrationForm()

    return render(request=request, template_name='account/register.html', context={'user_form': user_form})


@login_required
def edit(request: HttpRequest):
    template_name = 'account/edit.html'

    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request=request, template_name=template_name, context=context)


@login_required
def user_list(request: HttpRequest):
    template_name = 'account/user/list.html'
    users = User.objects.filter(is_active=True)

    context = {
        'users': users,
        'section': 'people'
    }

    return render(request=request, template_name=template_name, context=context)


@login_required
def user_detail(request: HttpRequest, username: str):
    template_name = 'account/user/detail.html'
    user = get_object_or_404(User,
                             username=username,
                             is_active=True)

    context = {
        'user': user,
        'section': 'people'
    }

    return render(request=request, template_name=template_name, context=context)


@require_POST
@login_required
def user_follow(request: HttpRequest):
    user_id = request.POST.get('id')
    action = request.POST.get('action')

    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if int(user_id) == request.user.id:
                return JsonResponse({'status': 'error'})
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user,
                                              user_to=user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})

    return JsonResponse({'status': 'error'})
