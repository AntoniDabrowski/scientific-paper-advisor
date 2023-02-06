from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('expandleft', views.expand_left, name='expandleft'),
    path('expandright', views.expand_right, name='expandright')
]