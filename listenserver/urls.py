"""listenserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from listenapi.views import register_user, login_user
from listenapi.views import Categories, Comments, Connections, Excerpts, Goals, Musicians, Recordings, CurrentUser
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'categories', Categories, 'category')
router.register(r'comments', Comments, 'comment')
router.register(r'connections', Connections, 'connection')
router.register(r'currentuser', CurrentUser, 'musician')
router.register(r'excerpts', Excerpts, 'excerpt')
router.register(r'goals', Goals, 'goal')
router.register(r'musicians', Musicians, 'musician')
router.register(r'recordings', Recordings, 'recording')

urlpatterns = [
    # path('admin/', admin.site.urls), #not needed?
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework'))
]
