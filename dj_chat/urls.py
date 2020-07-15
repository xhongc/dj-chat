"""charles URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.staticfiles import views
from django.urls import path, re_path
from django.views.generic import TemplateView
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from chat.views import FriendsViewsets, ChatLogViewsets, ChatRoomViewsets, PersonalChatLogViewsets, UserProfileViewsets, \
    RegisterViewsets
from utils.channelsmiddleware import LoginObtainJSONWebToken

router = DefaultRouter()
router.register(r'friends', viewset=FriendsViewsets, basename='friends')
router.register(r'chat_log', viewset=ChatLogViewsets, basename='chat_log')
router.register(r'personal_chat_log', viewset=PersonalChatLogViewsets, basename='personal_chat_log')
router.register(r'chat_room', viewset=ChatRoomViewsets, basename='chat_room')
router.register(r'user_profile', viewset=UserProfileViewsets, basename='user_profile')
router.register(r'register', viewset=RegisterViewsets, basename='register')

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path('^api/', include(router.urls)),
    re_path(r'^docs/', include_docs_urls(title='API & Dog', description='API文档', public=True)),
    re_path(r'^api-token-auth/', LoginObtainJSONWebToken.as_view()),
    path('', include('chat.urls'), name='chat-url'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', views.serve),
        re_path(r'^src/(?P<path>.*)$', views.serve),
    ]
