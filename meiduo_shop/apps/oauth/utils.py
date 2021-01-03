#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-12-20 22:58:50
@LastEditTime: 2020-12-20 23:34:14
@LastEditors: 张涛
@Description: openid加密签名
@FilePath: /meiduo_shop/apps/oauth/utils.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

from meiduo_shop.apps.oauth import constants


def generate_access_token(openid):
    """openid签名认证"""
    serializer = Serializer(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)
    # 准备签名数据
    data = {'openid': openid}
    # 加密数据
    token = serializer.dumps(data)
    return token.decode()


def check_access_token(access_token):
    """openid反序列化"""
    serializer = Serializer(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)
    try:
        data = serializer.load(access_token)
    except BadData:
        return None
    else:
        return data.get('openid')
