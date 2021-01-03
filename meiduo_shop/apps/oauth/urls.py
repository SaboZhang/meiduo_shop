#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-12-20 19:15:32
@LastEditTime: 2020-12-20 21:03:05
@LastEditors: 张涛
@Description: 授权登录接口路径配置
@FilePath: /meiduo_shop/apps/oauth/urls.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.urls import path

from .import views


urlpatterns = [
    path('qq/login/', views.QQOAuthUrlView.as_view()),
    path('oauth_callback/', views.QQAuthLoginView.as_view()),
]
