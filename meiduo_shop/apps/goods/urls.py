#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-22 00:00:47
@LastEditTime: 2020-11-22 11:03:51
@LastEditors: 张涛
@Description: 商品URL
@FilePath: /meiduo_shop/apps/goods/urls.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.urls import path
from meiduo_shop.apps.goods import views


urlpatterns = [
    path('', views.index, name='index')
]
