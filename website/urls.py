from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('construction/', views.construction, name='construction'),
    path('gallery/', views.gallery, name='gallery'),
    path('about/', views.about, name='about'),
]