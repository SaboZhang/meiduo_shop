#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-22 21:40:30
@LastEditTime: 2020-11-22 22:44:12
@LastEditors: 张涛
@Description: contents页面
@FilePath: /meiduo_shop/apps/contents/views.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.shortcuts import render
from django.views.generic import View


class IndexView(View):
    """首页内容"""
    def get(self, request):
        return render(request, 'index.html')
