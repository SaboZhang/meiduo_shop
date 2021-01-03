#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-21 01:18:00
@LastEditTime: 2020-11-26 01:09:46
@LastEditors: 张涛
@Description: 验证码url
@FilePath: /meiduo_shop/apps/verifications/urls.py
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
from django.urls import re_path
from . import views

urlpatterns = [
    # 图片验证码
    re_path(r'^image_code/(?P<uuid>[\w-]+)/$', views.ImageCode.as_view()),
    # # 手机验证码
    re_path(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SmsCode.as_view()),
]
