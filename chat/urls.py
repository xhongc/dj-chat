from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('video/', views.play_video, name='video'),
    path('video2/', views.stream_video, name='video2'),

]
