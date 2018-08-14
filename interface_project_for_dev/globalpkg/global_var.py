#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'shouke'

import time
import sys
from globalpkg.log import logger
from globalpkg.mydb import MyDB
from globalpkg.mytestlink import TestLink
from globalpkg.othertools import OtherTools

__all__ = ['global_headers', 'global_openId', 'global_serial', 'global_protocol_version',
           'global_product_version', 'saofudb', 'testdb', 'mytestlink',
           'other_tools', 'executed_history_id', 'testcase_report_tb', 'case_step_report_tb',
           'global_customer_Id', 'global_shop_Id', 'global_componentAppId', 'global_appId'
           ]

# 根据自己的实际需要进行合理的调整
if sys.argv[1] == '1':
    logger.info('当前运行环境：测试环境')
    logger.info('正在初始化数据库[名称：SAOFUDB1]对象')
    saofudb = MyDB('./config/dbconfig.conf', 'SAOFUDB1')
elif sys.argv[1] == '2':
    logger.info('已选择运行环境：预发布环境')
    logger.info('正在初始化数据库[名称：SAOFUDB2]对象')
    saofudb = MyDB('./config/dbconfig.conf', 'SAOFUDB2')

logger.info('正在初始化数据库[名称：TESTDB]对象')
testdb = MyDB('./config/dbconfig.conf', 'TESTDB')

logger.info('正在获取testlink')
mytestlink = TestLink().get_testlink()

other_tools = OtherTools()

executed_history_id = time.strftime('%Y%m%d%H%M%S', time.localtime())  # 流水记录编号
# testcase_report_tb = 'testcase_report_tb' + str(executed_history_id)
# case_step_report_tb = 'case_step_report_tb' + str(executed_history_id)
testcase_report_tb = 'testcase_report_tb'
case_step_report_tb = 'case_step_report_tb'

# 请求都携带的公用请求头、请求参数
if sys.argv[1] == '1':  # 测试环境的全局变量
    global_headers = {
        'saofu.client.test.saofu.cn': {'DeviceId': '864212016072809', 'Token': '5aa72c12-ae65-4105-8537-71a70cbc6b4d',
                                       'Content-Type': 'application/json'},
        'm.test.saofu.cn': {'Cookie': '10549840601068216320=ous64uC-ghJ9oTcASOu3Lucm-yxQ'}}
    # 's.test.saofu.cn': {'Cookie':".TEST.SAOFU.CN_SHAREJSESSIONID=9414b4c5-3413-40e1-bdf1-22a4ca6a915a"}}
    global_serial = '10549840601068216320'
    global_openId = 'ous64uC-ghJ9oTcASOu3Lucm-yxQ'  # 玲珑OpenId
    global_product_version = '3.2.12C'
    global_protocol_version = '4.0'
    global_customer_Id = '166891'
    global_shop_Id = '42'
    global_componentAppId = 'wx3f310afa2e1d86ba'
    global_appId = 'wxe78eb2fe5839397a'

elif sys.argv[1] == '2':  # 预发布环境的全局变量
    global_headers = {'saofu.client.test.saofu.cn': {},
                      'm.test.saofu.cn': {'Cookie': '10549840601068216320=ous64uC-ghJ9oTcASOu3Lucm-yxQ'},
                      's.test.saofu.cn': {
                          'Cookie': "  .TEST.SAOFU.CN_SHAREJSESSIONID=4c709cfd-7a22-41b7-89c5-c20d13937884;"}}
    global_serial = '10549840601068216320'
    global_openId = 'ous64uC-ghJ9oTcASOu3Lucm-yxQ'
    global_product_version = '3.2.12C'
    global_protocol_version = '4.0'
    global_customer_Id = '166891'
    global_shop_Id = '42'
    global_componentAppId = 'wx3f310afa2e1d86ba'
    global_appId = 'wxe78eb2fe5839397a'
# 自己自由扩展和更改
