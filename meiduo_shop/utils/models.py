#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-12-20 17:46:37
@LastEditTime: 2020-12-20 17:53:36
@LastEditors: 张涛
@Description: 一句话描述
@FilePath: /meiduo_shop/utils/models.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.db import models


class BaseModel(models.Model):
    """模型补充字段"""
    creat_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateField(auto_now_add=True, verbose_name='更新时间')

    class Meta:
        abstract = True
