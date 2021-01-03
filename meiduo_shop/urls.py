#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-21 01:18:00
@LastEditTime: 2021-01-03 16:20:26
@LastEditors: 张涛
@Description: 主URL配置
@FilePath: /meiduo_shop/urls.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
"""meiduo_shop URL Configuration

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
# from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('user/', include(('meiduo_shop.apps.users.urls', 'meiduo_shop.apps.users'), namespace='user')),
    path('', include(('meiduo_shop.apps.contents.urls', 'meiduo_shop.apps.contents'), namespace='contents')),
    path('verify/', include('meiduo_shop.apps.verifications.urls')),
    path('', include('meiduo_shop.apps.oauth.urls')),
    path('', include('meiduo_shop.apps.area.urls')),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon')),

]
