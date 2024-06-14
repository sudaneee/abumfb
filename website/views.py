from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import *

def home(request):
    return render(request, 'website/index.html')

def construction(request):
    return render(request, 'website/error.html')

def gallery(request):
    gallerys = Gallery.objects.all()
    context = {
        'gallerys': gallerys,
    }
    return render(request, 'website/gallery.html', context)


def about(request):
    return render(request, 'website/about-us.html')