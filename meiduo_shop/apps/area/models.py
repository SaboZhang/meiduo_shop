#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-12-26 23:20:59
@LastEditTime: 2020-12-26 23:24:23
@LastEditors: 张涛
@Description: 省市区数据模型
@FilePath: /meiduo_shop/apps/area/models.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.db import models

# Create your models here.


class Area(models.Model):
    """省市区"""
    name = models.CharField(max_length=20, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name='上级行政区划')
    short_name = models.CharField(max_length=20, verbose_name='简称')

    class Meta:
        db_table = 'sys_areas'
        verbose_name = '省市区'
        verbose_name_plural = '省市区'

    def __str__(self):
        return self.name
