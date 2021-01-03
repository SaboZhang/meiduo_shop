#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-12-01 23:47:18
@LastEditTime: 2020-12-26 20:43:04
@LastEditors: 张涛
@Description: 用户认证
@FilePath: /meiduo_shop/apps/users/utils.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadData

from . import constants
from meiduo_shop.apps.users.models import User


def get_user_by_account(account):
    """通过用户名查询用户"""
    try:
        if re.match(r'^(?:(?:\+|00)86)?1(?:(?:3[\d])|(?:4[5-7|9])|(?:5[0-3|5-9])|(?:6[5-7])|(?:7[0-8])|(?:8[\d])|(?:9[1|8|9]))\d{8}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileBackend(ModelBackend):
    """自定义用户认证"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        """重写用户认证方法"""
        # 判断是用户名还是手机号
        user = get_user_by_account(username)
        if user and user.check_password(password):
            return user
        else:
            return None


def generate_verify_email_url(user):
    """邮箱激活链接"""
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id': user.id, 'email': user.email}
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url


def check_verify_email_token(token):
    """反序列化获取用户"""
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user
