#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-21 21:21:48
@LastEditTime: 2020-12-27 00:44:46
@LastEditors: 张涛
@Description: 用户URL配置
@FilePath: /meiduo_shop/apps/area/urls.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.urls import path
from . import views


urlpatterns = [

    path('areas/', views.AreaView.as_view(), name='area')
]
