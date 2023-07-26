from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request: HttpRequest):
    template_name = 'account/dashboard.html'
    return render(request=request, template_name=template_name, context={'section': 'dashboard'})
