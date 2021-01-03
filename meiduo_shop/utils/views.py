#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-12-23 22:03:59
@LastEditTime: 2020-12-23 22:10:51
@LastEditors: 张涛
@Description: 未登录响应json数据扩展类
@FilePath: /meiduo_shop/utils/views.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django import http

from meiduo_shop.utils.response_code import RETCODE


class LoginRequiredJsonMixin(LoginRequiredMixin):
    """用户是否登录响应json"""
    def handle_no_permission(self):

        return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})
