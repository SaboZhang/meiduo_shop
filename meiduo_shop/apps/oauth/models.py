#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-12-20 17:57:03
@LastEditTime: 2020-12-20 18:01:28
@LastEditors: 张涛
@Description: 一句话描述
@FilePath: /meiduo_shop/apps/oauth/models.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.db import models

from meiduo_shop.apps import users
from meiduo_shop.utils.models import BaseModel
# Create your models here.


class OauthQQUser(BaseModel):
    """QQ登录模型"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'sys_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name
