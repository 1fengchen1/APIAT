#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'laiyu'

import json
import time
import configparser
import sys

from globalpkg.log import logger
from testcase import TestCase
from testsuite import TestSuite
from httpprotocol import MyHttp
from globalpkg.global_var import *


# 根据用例行某个用例
def run_testcase_by_id(testcase_id, httpobj=None, testplan='无计划'):
    try:
        testcase_info = mytestlink.getTestCase(testcase_id)  # 获取测试用例基本信息
        logger.info('获取测试用例信息 %s' % testcase_info)
    except Exception as e:
        logger.error('获取用例信息失败 %s,,暂停执行该用例' % e)
        return ('Fail', [('global_funtion_module', '获取用例信息失败 %s' % e)])
    # 获取用例所在套件和项目名称
    response = mytestlink.getFullPath([int(testcase_id)])
    response = response[str(testcase_id)]
    testsuite_name = ''
    for suit in response[1:]:
        testsuite_name = testsuite_name + '-' + suit
        testsuite_name = testsuite_name.lstrip('-')
    project_name = response[0]

    # 构造测试用例对象
    testcase_name = testcase_info[0]['name']
    testcase_steps = testcase_info[0]['steps']
    testcase_isactive = int(testcase_info[0]['active'])
    testsuite_id = int(testcase_info[0]['testsuite_id'])
    preconditions = testcase_info[0]['preconditions']
    tc_external_id = testcase_info[0]['full_tc_external_id']
    testcase_obj = TestCase(testcase_id, testcase_name, testcase_steps, testcase_isactive, project_name, testsuite_id,
                            tc_external_id, preconditions)

    if httpobj:
        myhttp = httpobj
    else:
        myhttp = get_http_conf_of_project(project_name)
        if not myhttp:
            logger.critical('用例所在项目配置存在问题，停止执行该用例')
            return ('Block', [('golbal_function_module', '用例所在项目配置存在问题，停止执行该用例')])
    try:
        sql_insert = 'INSERT INTO ' + testcase_report_tb + '(executed_history_id, testcase_id, testcase_name, testsuit, testplan, project, runresult, runtime, tc_external_id)' \
                                                           ' VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        data = (executed_history_id, testcase_id, testcase_name, testsuite_name, testplan, project_name, 'Block',
                '0000-00-00 00:00:00', tc_external_id)
        logger.info('记录测试用例到测试用例报表')
        testdb.execute_insert(sql_insert, data)

        logger.info('开始执行测试用例[id=%s，name=%s]' % (testcase_id, testcase_name))
        run_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # 记录运行时间
        case_executed_history_id = time.strftime('%Y%m%d%H%M%S', time.localtime())  # 流水记录编号
        testcase_run_result = testcase_obj.run_testcase(myhttp, testplan, case_executed_history_id)

        logger.info('正在更新用例执行结果')
        sql_update = 'UPDATE ' + testcase_report_tb + ' SET runresult=\"%s\", runtime=\"%s\",' \
                                                      ' case_exec_history_id=\"%s\"' \
                                                      ' WHERE executed_history_id = %s and testcase_id = %s' \
                                                      ' AND project=\'%s\' AND testplan=\'%s\''
        data = (
            testcase_run_result[0], run_time, str(case_executed_history_id), executed_history_id, testcase_id,
            project_name,
            testplan)
        testdb.execute_update(sql_update, data)

        logger.info('指定用例[%s]已执行完' % testcase_name)

        return testcase_run_result
    except Exception as e:
        logger.error('运行用例出错 %s' % e)
        return ('Fail', [('golbal_function_module', '%s' % e)])


def get_http_conf_of_project(project_name):
    try:
        testproject = mytestlink.getTestProjectByName(project_name)
    except Exception as e:
        logger.error('测试项目[project：%s]获取失败，暂时无法执行：%s' % (project_name, e))
        return None

    project_notes = other_tools.conver_date_from_testlink(testproject['notes'])
    logger.info('正在读取测项目[project：%s]的协议，host，端口配置...' % project_name)
    testproject_conf = project_notes

    logger.info('成功读取配置信息：%s' % testproject_conf)
    if '' == testproject_conf:
        logger.error('测试项目[project：%s]未配置协议，host，端口信息，暂时无法执行' % project_name)
        return None

    try:
        notes = json.loads(testproject_conf)
        protocol = notes['protocol']
        host = notes['host']
        port = notes['port']
    except Exception as e:
        logger.error('测试项目[project：%s]协议，host，端口信息配置错误,暂时无法执行：%s' % (project_name, e))
        return None

    logger.info('正在构建项目的http对象')
    myhttp = MyHttp(protocol, host, port)
    return myhttp


def generate_runmode_conf():
    config = configparser.ConfigParser()
    parameters_list = [
        {"RUNMODE": "runmode"},
        {"PROJECTS": "project_mode"},
        {"PROJECTS": "projects"},
        {"PLANS": "project"},
        {"PLANS": "plans"},
        {"TESTSUITES": "testsuites"},
        {"TESTCASES": "case_id_list"},
        {"GLOBALCASES": "global_cases_str"}]

    if sys.argv[1] == '1':
        run_mode_conf_file = './config/runmodeconfig_test.conf'
    elif sys.argv[1] == '2':
        run_mode_conf_file = './config/runmodeconfig_release.conf'

    i = 2
    for parameter in parameters_list:

        section = list(parameter.keys())[0]     # key值
        option = parameter.get(section)         # value值

        if not config.has_section(section):
            config.add_section(section)
        config.set(section, option, sys.argv[i])
        i = i + 1

    # print(config)
    with open(run_mode_conf_file, 'w', encoding='UTF-8') as configfile:
        config.write(configfile)

# 生成的配置文件如下
# [RUNMODE]
# runmode = 3
# 
# [PROJECTS]
# project_mode = 2
# projects = [ 'pj_shop', 'pj_wechatno']
# 
# [PLANS]
# project = pj_wechatno
# plans = ['plan1_of_wechatno','pj_wechatno']
# 
# [TESTSUITES]
# testsuites =  147:pj-pos登录接口
# 
# [TESTCASES]
# case_id_list = [148]
# 
# [GLOBALCASES]
# global_cases_str = pj_pos||148:test-n-登陆掌贝pos机#pj_shop||969:登录商户后台|275:打开订单管理页面
