from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

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


def blog(request):
    blog_list = Blog.objects.all()
    blogss = blog_list
    page = request.GET.get('page', 1)

    paginator = Paginator(blog_list, 2)  # Show 5 blogs per page
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)

    context = {
        'blogs': blogs,
        'blogss': blogss,
    }
    return render(request, 'website/blog.html', context)


def single_blog(request, pk):
    blog = Blog.objects.get(id=pk)
    blogs = Blog.objects.all()
    context = {
        'blog': blog,
        'blogs': blogs
    }
    return render(request, 'website/single-blog.html', context)


def events(request):
    pass

def contact(request):
    return render(request, 'website/contact.html')


def single_service(request, pk):
    service = Service.objects.get(id=pk)
    services = Service.objects.all()

    context = {
        'service': service,
        'services': services,
    }
    
    return render(request, 'website/single-service.html', context)