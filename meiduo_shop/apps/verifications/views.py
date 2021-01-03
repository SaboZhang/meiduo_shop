#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-23 20:45:23
@LastEditTime: 2020-11-30 22:46:42
@LastEditors: 张涛
@Description: 验证码视图
@FilePath: /meiduo_shop/apps/verifications/views.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.views.generic import View
from django_redis import get_redis_connection
from django import http
import random, logging


from meiduo_shop.apps.verifications.libs.captcha.captcha import captcha
from meiduo_shop.utils.response_code import RETCODE
from meiduo_shop.apps.verifications import constants
from celery_tasks.sms.tasks import send_sms_code
# Create your views here.


logger = logging.getLogger('django')


class SmsCode(View):
    """短信验证码"""

    def get(self, request, mobile):
        # 接收参数
        imgae_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 校验参数
        if not all([imgae_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必要的参数')
        # 获取图形验证码
        redis_conn = get_redis_connection('verify_code')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '短信验证发送过于频繁'})
        image_conde_server = redis_conn.get('img_%s' % uuid)
        if image_conde_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已过期'})
        # 删除图形验证码缓存
        try:
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            logger.info(e)
        # 比较图形验证码
        image_conde_server = image_conde_server.decode()
        if image_conde_server.lower() != imgae_code_client.lower():
            print(image_conde_server)
            print(imgae_code_client)
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '验证码输入错误'})
        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        pl = redis_conn.pipeline()
        # redis_conn.setex('code_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.setex('code_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行
        pl.execute()
        # AliyunSms().send_sms(mobile, sms_code, constants.SEND_SMS_TEMPLATE_ID)
        send_sms_code.delay(mobile, sms_code)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '短信发送成功'})


class ImageCode(View):
    """图片验证码页面"""

    def get(self, request, uuid):
        # 生成验证码
        text, image = captcha.generate_captcha()
        # 保存验证码
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return http.HttpResponse(image, content_type='image/jpg')
