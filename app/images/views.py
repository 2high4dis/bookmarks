from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST
from .forms import ImageCreateForm
from .models import Image


@login_required
def image_create(request: HttpRequest):
    template_name = 'images/image/create.html'

    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            messages.success(request, 'Image added successfully')
            return redirect(new_image.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)

    context = {
        'form': form,
        'section': 'images'
    }

    return render(request=request, template_name=template_name, context=context)


def image_detail(request: HttpRequest, id: int, slug: str):
    template_name = 'images/image/detail.html'

    image = get_object_or_404(Image, id=id, slug=slug)

    context = {
        'section': 'images',
        'image': image
    }

    return render(request=request, template_name=template_name, context=context)


@login_required
@require_POST
def image_like(request: HttpRequest):
    image_id = request.POST.get('id')
    action = request.POST.get('action')

    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass

    return JsonResponse({'status': 'error'})
