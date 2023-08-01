from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .forms import ImageCreateForm
from .models import Image
from actions.utils import create_action
import redis
from django.conf import settings

r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


@login_required
def image_create(request: HttpRequest):
    template_name = 'images/image/create.html'

    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
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

    total_views = r.incr(f'image:{image.id}:views')

    r.zincrby('image_ranking', 1, image.id)

    context = {
        'section': 'images',
        'image': image,
        'total_views': total_views
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
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass

    return JsonResponse({'status': 'error'})


@login_required
def image_list(request: HttpRequest):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)

    context = {
        'section': 'images',
        'images': images
    }

    if images_only:
        return render(request=request,
                      template_name='images/image/list_images.html',
                      context=context)

    return render(request=request,
                  template_name='images/image/list.html',
                  context=context)


@login_required
def image_ranking(request: HttpRequest):
    template_name = 'images/image/ranking.html'

    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]

    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))

    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))

    context = {
        'section': 'images',
        'most_viewed': most_viewed
    }

    return render(request=request, template_name=template_name, context=context)
