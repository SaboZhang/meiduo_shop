#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-30 22:42:29
@LastEditTime: 2020-11-30 23:57:43
@LastEditors: 张涛
@Description: 定义celery任务
@FilePath: /celery_tasks/sms/tasks.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
import logging

from celery_tasks.sms.send_code import AliyunSms
from . import constants
from ..main import celery_app


logger = logging.getLogger('django')


@celery_app.task(bind=True, name='send_sms_code', retry_backoff=3)
def send_sms_code(self, mobile, sms_code):

    try:
        AliyunSms().send_sms(mobile, sms_code, constants.SEND_SMS_TEMPLATE_ID)
    except Exception as e:
        logger.error(e)
        # 重试
        raise self.retry(exc=e, max_retries=3)
