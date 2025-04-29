from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('construction/', views.construction, name='construction'),
    path('gallery/', views.gallery, name='gallery'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('blog/<int:pk>/', views.single_blog, name='single-blog'),
    path('contact/', views.contact, name='contact'),
    path('service/<int:pk>/', views.single_service, name='single-service'),
]
