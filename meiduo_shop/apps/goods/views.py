#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-22 00:00:17
@LastEditTime: 2020-11-22 11:04:00
@LastEditors: 张涛
@Description: 商品展示
@FilePath: /meiduo_shop/apps/goods/views.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.shortcuts import render


# 用户首页
def index(request):
    return render(request, 'index.html')
