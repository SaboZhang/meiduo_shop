#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-12-26 15:55:15
@LastEditTime: 2020-12-26 19:26:34
@LastEditors: 张涛
@Description: 验证邮件发送任务
@FilePath: /celery_tasks/email/tasks.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from django.conf import settings
from django.core.mail import send_mail
import logging

from celery_tasks.main import celery_app


logger = logging.getLogger('django')


@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    """发送验证邮件"""
    subject = '美多商城邮箱验证'
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的绑定邮箱为：%s 。请在24小时内点击此下方链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url) + \
                   '<p></p>' \
                   '<p>本邮件为系统自动发送，请勿直接回复</p>'
    try:
        send_mail(subject, '', settings.EMAIL_FROM, [to_email], html_message=html_message)
    except Exception as e:
        logger.error(e)
        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)
