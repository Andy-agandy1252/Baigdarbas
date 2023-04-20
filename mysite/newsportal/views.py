from django.shortcuts import render
from django.http import HttpResponse
from .models import Article

from django.shortcuts import render

def index(request):
    articles = Article.objects.all()
    context = {'articles': articles}
    return render(request, 'index.html', context)
