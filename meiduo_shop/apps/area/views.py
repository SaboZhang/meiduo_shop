#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-12-26 23:20:59
@LastEditTime: 2020-12-27 01:44:15
@LastEditors: 张涛
@Description: 省市区联动
@FilePath: /meiduo_shop/apps/area/views.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django import http
from django.shortcuts import render
from django.views.generic import View
import logging

# Create your views here.
from meiduo_shop.apps.area.models import Area
from meiduo_shop.utils.response_code import RETCODE


logger = logging.getLogger('django')


class AreaView(View):
    """省市区视图"""
    def get(self, request):
        area_id = request.GET.get('area_id')
        if not area_id:
            # 提供省份数据
            try:
                province_model_list = Area.objects.filter(parent__isnull=True)
                province_list = []
                for province_model in province_model_list:
                    province_dict = {
                        'id': province_model.id,
                        'name': province_model.name
                    }
                    province_list.append(province_dict)
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '获取省份数据失败'})
        else:
            # 根据省份ID查询数据
            try:
                parent_model = Area.objects.get(id=area_id)
                subs_models_list = parent_model.subs.all()
                subs = []
                for subs_model in subs_models_list:
                    subs_dict = {
                        'id': subs_model.id,
                        'name': subs_model.name
                    }
                    subs.append(subs_dict)
                sub_data = {
                    'id': parent_model.id,
                    'name': parent_model.name,
                    'subs': subs
                }
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市数据查询错误'})
