#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-23 23:33:54
@LastEditTime: 2020-11-26 00:11:09
@LastEditors: 张涛
@Description: 一句话描述
@FilePath: /meiduo_shop/apps/verifications/constants.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
# 图形验证码有效期，单位：秒
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码有效期，单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 短信模板
SEND_SMS_TEMPLATE_ID = 'SMS_205810638'

# 60s内是否重复发送的标记
SEND_SMS_CODE_INTERVAL = 60
