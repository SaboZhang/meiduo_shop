#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: 张涛
@Date: 2020-11-30 22:05:23
@LastEditTime: 2020-11-30 22:38:26
@LastEditors: 张涛
@Description: Celery配置文件
@FilePath: /celery_tasks/config.py
@世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
"""
# 创建配置文件 指定中间人、消息队列、任务队列
broker_url = 'redis://192.168.3.12:6379/10'
