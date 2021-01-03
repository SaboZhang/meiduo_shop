#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-21 20:10:45
@LastEditTime: 2021-01-03 21:42:12
@LastEditors: 张涛
@Description: 一句话描述
@FilePath: /meiduo_shop/apps/users/views.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
import json
import logging
import re

from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django_redis import get_redis_connection

from celery_tasks.email.tasks import send_verify_email
from meiduo_shop.apps.users.models import User, Address
from meiduo_shop.apps.users.utils import generate_verify_email_url, check_verify_email_token
from meiduo_shop.utils.response_code import RETCODE
from meiduo_shop.utils.views import LoginRequiredJsonMixin
from . import constants

logger = logging.getLogger('django')


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """显示注册页面"""

        # 买家注册页面
        return render(request, 'register.html')

    def post(self, request):
        """用户注册请求"""
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        client_sms_code = request.POST.get('sms_code')
        allow = request.POST.get('allow')
        # 数据校验
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必要的参数')
        if not re.match(r'^[a-zA-Z0-9_-]{4,16}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 校验密码是否一致
        if not (password == password2):
            return http.HttpResponseForbidden('密码不一致')
        if not re.match(
                r'^(?:(?:\+|00)86)?1(?:(?:3[\d])|(?:4[5-7|9])|(?:5[0-3|5-9])|(?:6[5-7])|(?:7[0-8])|(?:8[\d])|(?:9[1|8|9]))\d{8}$',
                mobile):
            return http.HttpResponseForbidden('请输入正确格式的手机号')
        # 校验验证码
        redis_conn = get_redis_connection('verify_code')
        server_sms_code = redis_conn.get('code_%s' % mobile)
        if server_sms_code is None:
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已过期'})
        if client_sms_code != server_sms_code.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '验证码输入有误'})
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')
        # return render(request, 'register.html', {'register_errmsg': '注册失败'})
        # 保存用户信息
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError as e:
            logger.info(e)
            return render(request, 'register.html', {'register_errmsg': '注册失败'})
        # 状态保持
        login(request, user)
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=3600 * 24 * 7)
        return response


class UsernameIsUnique(View):
    """用户名唯一验证"""

    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobileUnique(View):
    """手机号唯一验证"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class LoginView(View):
    """登录视图"""

    def get(self, request):
        """提供用户登录页面"""
        return render(request, 'login.html')

    def post(self, request):
        """实现用户登录逻辑"""
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确用户名/手机号')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码长度为8-20位')
        # 用户认证
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '账号或密码错误'})
        # 状态保持
        login(request, user)
        # 记住密码
        if remembered != 'on':
            # 单位为秒
            request.session.set_expiry(0)
        else:
            # None 默认为两周
            request.session.set_expiry(None)
        # 展示登录信息
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=3600 * 24 * 7)

        return response


class LogoutView(View):
    """用户退出登录"""

    def get(self, request):
        logout(request)

        # 删除cookie
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')

        return response


class UserCenterView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """进入个人中心"""
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context)


class EmailView(LoginRequiredJsonMixin, View):
    """邮箱验证"""

    def put(self, request):
        # 将用户传入的邮箱保存到email字段
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        email = json_dict.get('email')
        if not re.match(
                r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
                email):
            return http.HttpResponseForbidden('邮箱格式错误')
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '网络错误'})
        verify_url = generate_verify_email_url(request.user)
        send_verify_email.delay(email, verify_url)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class VerifyEmailView(View):
    """邮箱绑定校验"""

    def get(self, request):
        token = request.GET.get('token')
        # 判断是否存在token
        if not token:
            return http.HttpResponseForbidden('缺少token')
        # 反序列化token
        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseBadRequest('无效的token')
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('邮箱激活失败')
        # 激活成功重定向到用户中心
        return redirect(reverse('user:info'))


class AddressView(LoginRequiredMixin, View):
    """用户收获地址视图"""

    def get(self, request):
        """获取收货地址页面"""
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)
        address_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_list.append(address_dict)
        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_list,
        }
        return render(request, 'user_center_site.html', context)


class CreateAddressView(LoginRequiredJsonMixin, View):
    """新增用户地址"""

    def post(self, request):
        # 判断用户地址数量是否超过上限
        count = request.user.addresses.count()
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.DBERR,
                                      'errmsg': '地址数量超过上限'})
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')
        # 保存地址
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '网络错误'})
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增成功', 'address': address_dict})


class UpdateAddressView(LoginRequiredJsonMixin, View):
    """更新/逻辑删除地址信息"""
    def put(self, request, address_id):
        """更新地址"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            address = Address.objects.get(id=address_id)
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新成功', 'address': address_dict})
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '网络错误'})

    def delete(self, request, address_id):
        """删除地址信息"""
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除成功'})


class DefaultAddressView(LoginRequiredJsonMixin, View):
    """设置默认地址"""
    def put(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置成功'})


class UpdateTitleView(LoginRequiredJsonMixin, View):
    """更新title"""
    def put(self, request, address_id):
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        try:
            address = Address.objects.get(id=address_id)
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '处理失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '标题更新成功'})
