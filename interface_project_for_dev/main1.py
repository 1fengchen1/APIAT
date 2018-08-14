#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 这是不用在Jenkins上配置的代码
__author__ = 'shouke'

import datetime
import json
import configparser
import sys

from globalpkg.log import logger
from globalpkg.global_var import *
from globalpkg.global_function import run_testcase_by_id
from globalpkg.global_function import get_http_conf_of_project

from config.runmodeconfig import RunModeConfig
from testsuite import TestSuite
from testplan import TestPlan
from testproject import TestProject
from htmlreporter import HtmlReport
from sendmail import MyMail

if __name__ == '__main__':
    # 记录测试开始时间
    start_time = datetime.datetime.now()

    create_testcase_reporter_tb_sql = 'CREATE TABLE IF NOT EXISTS ' + testcase_report_tb + '\
                                         (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,\
                                          executed_history_id varchar(50) NOT NULL,\
                                          testcase_id int NOT NULL,\
                                          testcase_name varchar(40) NOT NULL,\
                                          testsuit varchar(40),\
                                          testplan varchar(40),\
                                          project varchar(40),\
                                          runresult varchar(20),\
                                          runtime datetime,\
                                          case_exec_history_id varchar(50), \
                                          tc_external_id varchar(50))'
    create_case_step_reporter_tb_sql = 'CREATE TABLE IF NOT EXISTS ' + case_step_report_tb + '\
                                         (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,\
                                          executed_history_id varchar(50) NOT NULL,\
                                          testcase_id int NOT NULL,\
                                          testcase_name varchar(40) NOT NULL,\
                                          testplan varchar(40) NOT NULL,\
                                          project varchar(40) NOT NULL,\
                                          step_id int,\
                                          step_num int NOT NULL,\
                                          step_action varchar(1000), \
                                          expected_results varchar(1000),\
                                          runresult varchar(10),\
                                          reason varchar(2000),\
                                          protocol_method varchar(40) ,\
                                          protocol varchar(40),\
                                          host varchar(40),\
                                          port int,\
                                          runtime datetime)'

    logger.info('正在创建测试用例报告报表')
    testdb.execute_create(create_testcase_reporter_tb_sql)

    logger.info('正在创建测试步骤报告报表')
    testdb.execute_create(create_case_step_reporter_tb_sql)

    logger.info('正在读取运行模式配置')
    if sys.argv[1] == '1':
        run_mode_conf = RunModeConfig('./config/runmodeconfig_test.conf')
    elif sys.argv[1] == '2':
        run_mode_conf = RunModeConfig('./config/runmodeconfig_release.conf')
    run_mode = int(run_mode_conf.get_run_mode())

    logger.info('正在获取运行全局初始化用例……')
    global_cases_list = run_mode_conf.get_global_cases()

    project_httpobj_dict = {}
    for item in global_cases_list:
        project_name = item[0]
        cases_list = item[1]
        httpobj = get_http_conf_of_project(project_name)
        if not httpobj:
            logger.critical('初始化用例所在项目配置存在问题，提前终止程序运行')
            exit()
        else:
            logger.info('正在运行项目："%s"的全局初始化用例id列表：%s' % (project_name, cases_list))
            project_httpobj_dict[project_name] = httpobj
            for case_id in cases_list:
                res = run_testcase_by_id(case_id, httpobj)
                logger.info('用例[%s]运行结果：%s' % (id, res))

    if 1 == run_mode:
        logger.info('按项目运行测试')
        project_mode = run_mode_conf.get_project_mode()
        testplans_name_list = []
        if 1 == project_mode:
            logger.info('运行所有项目')
            projects = mytestlink.getProjects()
            for project in projects:
                # 构造项目对象
                active_status = project['active']
                project_name = project['name']
                project_notes = other_tools.conver_date_from_testlink(project['notes'])
                project_id = int(project['id'])
                project_obj = TestProject(active_status, project_name, project_notes, project_id)

                # 构造http对象
                if project_name in project_httpobj_dict.keys():
                    myhttp = project_httpobj_dict[project_name]
                else:
                    myhttp = get_http_conf_of_project(project_name)
                    if not myhttp:
                        logger.critical('项目配置存在问题，已被忽略，不执行')
                        continue
                logger.info('正在执行测试项目[id：%s, project：%s]' % (project_id, project_name))
                project_obj.run_testproject(myhttp)
        elif 2 == project_mode:
            logger.info('运行指定项目')
            testprojects_name_list = eval(run_mode_conf.get_projects())
            for testproject_name in testprojects_name_list:
                try:
                    print('*******************%s*********************' % testproject_name)
                    testproject = mytestlink.getTestProjectByName(testproject_name)
                except Exception as e:
                    logger.error('测试项目[project：%s]获取失败，暂时无法执行：%s' % (testproject_name, e))
                    continue

                # 构造项目对象
                active_status = testproject['active']
                project_name = testproject['name']
                project_notes = other_tools.conver_date_from_testlink(testproject['notes'])
                project_id = int(testproject['id'])
                project_obj = TestProject(active_status, project_name, project_notes, project_id)

                # 构造http对象
                if project_name in project_httpobj_dict.keys():
                    myhttp = project_httpobj_dict[project_name]
                else:
                    myhttp = get_http_conf_of_project(project_name)
                    if not myhttp:
                        logger.critical('项目配置存在问题，已忽略，不执行')
                        continue
                logger.info('正在执行测试项目[id：%s, project：%s]' % (project_id, project_name))
                project_obj.run_testproject(myhttp)
    elif 2 == run_mode:
        logger.info('按计划运行测试')
        project_of_plans = run_mode_conf.get_project_of_testplans()
        testplans_name_list = run_mode_conf.get_testplans()
        testplans_name_list = eval(testplans_name_list)
        logger.info('已获取配置的项目名称[name：%s]及对应的测试计划名称列表[list=%s]' % (project_of_plans, testplans_name_list))

        for testplan in testplans_name_list:
            # 构造测试计划对象
            try:
                testplan_info = mytestlink.getTestPlanByName(project_of_plans, testplan)
            except Exception as e:
                logger.error('测试计划[project：%s，testplan：%s]获取失败，暂时无法执行：%s' % (project_of_plans, testplan, e))
                continue

            testplan_name = testplan_info[0]['name']
            testplan_id = int(testplan_info[0]['id'])
            active_status = int(testplan_info[0]['active'])
            notes = other_tools.conver_date_from_testlink(testplan_info[0]['notes'])
            testplan_obj = TestPlan(testplan_name, testplan_id, active_status, notes, project_of_plans)

            # 构造http对象
            if project_of_plans in project_httpobj_dict.keys():
                myhttp = project_httpobj_dict[project_of_plans]
            else:
                myhttp = get_http_conf_of_project(project_of_plans)
                if not myhttp:
                    logger.critical('计划所在配置存在问题，跳过执行该计划')
                    continue
            logger.info('正在执行测试计划[project：%s，testplan：%s]' % (project_of_plans, testplan))
            testplan_obj.run_testplan(myhttp)
    elif 3 == run_mode:
        logger.info('按套件运行测试')
        testsuits_id_list = run_mode_conf.get_testsuits()
        logger.info('已获取配置的套件id列表：%s' % testsuits_id_list)

        for testsuite_id in testsuits_id_list:
            # 构造测试套件对象
            try:
                testsuite_info = mytestlink.getTestSuiteByID(testsuite_id)
            except Exception as e:
                logger.error('测试套件[id=%s]不存在，暂时无法执行' % testsuite_id)
                continue

            testsuite_name = testsuite_info['name']
            testsuite_details = other_tools.conver_date_from_testlink(testsuite_info['details'])
            project = mytestlink.getFullPath(testsuite_id)
            project_name = project[str(testsuite_id)][0]
            testsuite_obj = TestSuite(testsuite_id, testsuite_name, testsuite_details, project_name)

            logger.info('正在执行测试套件[id=%s ,name=%s]' % (testsuite_id, testsuite_name))
            # 构造http对象
            if project_name in project_httpobj_dict.keys():
                myhttp = project_httpobj_dict[project_name]
            else:
                myhttp = get_http_conf_of_project(project_name)
                if not myhttp:
                    logger.critical('套件所在项目配置存在问题，跳过执行该套件')
                    continue
            testsuite_obj.run_testsuite(myhttp)

    elif 4 == run_mode:
        logger.info('运行指定用例……')
        testcase_id_list = run_mode_conf.get_testcase_id_list()
        logger.info('待运行用例id列表：%s', testcase_id_list)
        for id in testcase_id_list:
            res = run_testcase_by_id(id)
            logger.info('用例[%s]运行结果：%s' % (id, res))

    logger.info('接口测试已执行完成，正在关闭数据库连接')
    testdb.close()
    saofudb.close()

    if 4 != run_mode:
        # 记录测试结束时间
        end_time = datetime.datetime.now()

        # 构造测试报告
        html_report = HtmlReport('Test Report', 'Interface_Autotest_Report')
        html_report.set_time_took(str(end_time - start_time))  # 计算测试消耗时间

        # 读取测试报告路径及文件名
        config = configparser.ConfigParser()
        config.read('./config/report.conf', encoding='utf-8')
        dir_of_report = config['REPORT']['dir_of_report']
        report_name = config['REPORT']['report_name']

        # 设置报告生成路
        html_report.mkdir_of_report(dir_of_report)

        # 生成测试报告
        html_report.generate_html(report_name)

        logger.info('生成测试报告成功')

        mymail = MyMail('./config/mail.conf')
        mymail.connect()
        mymail.login()
        mail_content = 'Hi，附件为接口测试报告，烦请查阅'
        mail_tiltle = '【测试报告】接口测试报告' + str(executed_history_id)
        logger.info(html_report.get_filename())
        attachments = set([html_report.get_filename()])

        logger.info('正在发送测试报告邮件...')
        mymail.send_mail(mail_tiltle, mail_content, attachments)
        mymail.quit()

        logger.info('发送邮件成功')
