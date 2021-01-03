#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-24 21:32:36
@LastEditTime: 2020-11-30 23:27:57
@LastEditors: 张涛
@Description: 一句话描述
@FilePath: /celery_tasks/sms/send_code.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import ast
import logging

from . import const


logger = logging.getLogger('django')


class AliyunSms:

    def __init__(self):
        self.accessKeyId = const.ACCESS_KEY_ID
        self.accessSecret = const.ACCESS_KEY_SECRET
        self.signName = const.SINGNNAME

    def _generate_request(self, phone_num, code, templateCode):
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(const.DOMAIN)
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')
        request.add_query_param('PhoneNumbers', phone_num)
        request.add_query_param('SignName', self.signName)
        request.add_query_param('TemplateCode', templateCode)
        request.add_query_param('TemplateParam', '{"code": ' + code + '}')
        return request

    def _generate_client(self):
        client = AcsClient(self.accessKeyId, self.accessSecret, 'cn-hangzhou')
        return client

    def send_sms(self, phone_num, code, templateCode):
        """
        发送短信验证码,返回Code字段的值
        :param phone_num: 手机号
        :param code: 验证码内容
        :param templateCode: 验证码模板
        :return:
        """
        client = self._generate_client()
        request = self._generate_request(phone_num, code, templateCode)
        try:
            response = client.do_action_with_exception(request)
            response = ast.literal_eval(response.decode())
            logger.info(response)
            if response.get('Code') == 'OK':
                return 0
            else:
                logger.info(response.get('Code'))
                return -1
        except ServerException as e:
            logger.error(e)
            return '由于系统维护，暂时无法注册！！！'
        except ClientException as e:
            logger.error(e)
            return '由于系统维护，暂时无法注册！！！'


# if __name__ == '__main__':
#     AliyunSms().send_sms('13821506212', '112233', 'SMS_205810638')
