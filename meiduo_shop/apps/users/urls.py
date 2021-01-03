#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-21 21:21:48
@LastEditTime: 2021-01-03 21:07:08
@LastEditors: 张涛
@Description: 用户URL配置
@FilePath: /meiduo_shop/apps/users/urls.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.urls import path, re_path
from . import views

urlpatterns = [

    path('register/', views.RegisterView.as_view(), name='register'),
    # 用户名唯一性验证路由
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameIsUnique.as_view()),
    # 手机号唯一性验证路由
    re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileUnique.as_view()),
    # 用户登录
    path('login/', views.LoginView.as_view(), name='login'),
    # 退出登录
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # 个人中心
    path('info/', views.UserCenterView.as_view(), name='info'),
    # email
    path('emails/', views.EmailView.as_view(), name='email'),
    # 激活验证
    path('emails/verification/', views.VerifyEmailView.as_view()),
    # 收货地址
    path('addresses', views.AddressView.as_view(), name='address'),
    # 新增收货地址
    path('addresses/create/', views.CreateAddressView.as_view()),
    # 更新数据
    re_path(r'addresses/(?P<address_id>\d+)/', views.UpdateAddressView.as_view(), name='update'),
    # 设置默认地址
    re_path(r'addresses/(?P<address_id>\d+)/default/', views.DefaultAddressView.as_view(), name='default'),
    # 更新标题
    re_path(r'addresses/(?P<address_id>\d+)/title/', views.UpdateTitleView.as_view(), name='title'),
]
