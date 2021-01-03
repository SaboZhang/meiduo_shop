#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-12-20 17:57:03
@LastEditTime: 2020-12-23 23:15:02
@LastEditors: 张涛
@Description: QQ授权登录
@FilePath: /meiduo_shop/apps/oauth/views.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
import logging
import re, json
import requests
from urllib.parse import urlencode

from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection

# Create your views here.
from .models import OauthQQUser
from .utils import generate_access_token, check_access_token
from ...utils.response_code import RETCODE
from meiduo_shop.apps.users.models import User

logger = logging.getLogger('django')


class QQOAuthUrlView(View):
    """获取QQ授权登录页面"""

    def get(self, request):
        # next表示从哪个页面进入登录页面
        next = request.GET.get('next')
        # 获取QQ授权登录页面地址
        oauth = OAuthQQ(client_id=settings.QQ_APP_ID,
                        client_secret=settings.QQ_APP_KEY,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()
        return http.JsonResponse(
            {'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


class QQAuthLoginView(View):
    """处理QQ授权登录回调"""

    def get(self, request):
        # 获取code
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('缺少code参数')
        oauth = OAuthQQ(client_id=settings.QQ_APP_ID,
                        client_secret=settings.QQ_APP_KEY,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 获取access_token
            access_token = oauth.get_access_token(code)
            # 获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')
        # 查询用户是否绑定
        self.get_user_info(access_token, settings.QQ_APP_ID, openid)
        try:
            oauth_user = OauthQQUser.objects.get(openid=openid)
        except OauthQQUser.DoesNotExist:
            # 未注册用户
            access_token_openid = generate_access_token(openid)
            context = {'access_token_openid': access_token_openid}
            return render(request, 'oauth_callback.html', context)
        else:
            qq_user = oauth_user.user
            # 状态保持
            login(request, qq_user)
            # 写入cookie
            next = request.GET.get('state')
            response = redirect(next)
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 7)

        return response

    def post(self, request):
        """用户绑定"""
        # 接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token = request.POST.get('access_token')

        # 校验参数
        # 判断参数是否齐全
        if not all([mobile, pwd, sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 判断openid是否有效
        openid = check_access_token(access_token)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '用户绑定超时'})
        # 保存注册信息
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户不存在
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            # 用户存在
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})
        # 绑定用户openid
        try:
            oauth_user = OauthQQUser.objects.create(openid=openid, user=user)
        except Exception as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'qq_login_errmsg', 'QQ登录失败,请稍后重试'})
        qq_user = oauth_user.user
        # 状态保持
        login(request, qq_user)
        # 写入cookie
        next = request.GET.get('state')
        response = redirect(next)
        response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 7)
        return response

    def get_user_info(self, access_token, oauth_consumer_key, openid):
        """获取用户QQ信息"""
        data_dict = {
            'access_token': access_token,
            'oauth_consumer_key': oauth_consumer_key,
            'openid': openid
        }
        # 构建url
        user_info_url = 'https://graph.qq.com/user/get_user_info?' + urlencode(data_dict)
        # 发送请求
        try:
            response = requests.get(user_info_url)

            # 提取数据
            data = response.text

            # 转化为字典
            data_dict = json.loads(data)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseBadRequest
        return data_dict
