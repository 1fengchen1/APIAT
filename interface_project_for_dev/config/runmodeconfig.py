#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'shouke'

import configparser
import json
from collections import OrderedDict

from globalpkg.log import logger


class RunModeConfig:
    def __init__(self, run_mode_conf):
        config = configparser.ConfigParser()

        # 从配置文件中读取运行模式
        config.read(run_mode_conf, encoding='utf-8-sig')
        try:
            self.run_mode = config['RUNMODE']['runmode']
            self.project_mode = int(config['PROJECTS']['project_mode'])
            self.projects = config['PROJECTS']['projects']
            self.testplans = config['PLANS']['plans']
            self.project_of_plans = config['PLANS']['project']
            self.testsuites = config['TESTSUITES']['testsuites']
            self.case_id_list = eval(config['TESTCASES']['case_id_list'])
            self.global_cases_str = config['GLOBALCASES']['global_cases_str']
            self.global_cases = []
        except Exception as e:
            logger.error('读取运行模式配置失败：%s' % e)
            exit()

    def get_run_mode(self):
        return self.run_mode

    def get_project_mode(self):
        return self.project_mode

    def get_projects(self):
        return self.projects

    def get_testplans(self):
        return self.testplans

    def get_project_of_testplans(self):
        return self.project_of_plans

    def get_testsuits(self):
        self.testsuites = self.testsuites.replace('：', ':')
        testsuites_list = self.testsuites.split('|')  # 拆分套件
        self.testsuites = []
        for testsuite in testsuites_list[:]:
            testsuite_list = testsuite.split(':')
            self.testsuites.append(int(testsuite_list[0]))
        return self.testsuites

    def get_testcase_id_list(self):
        return self.case_id_list

    def get_global_cases(self):
        self.global_cases_str = self.global_cases_str.replace('：', ':')  # 防止用户输入中文冒号
        temp_list = self.global_cases_str.split("#")  # 拆分出项目
        for item in temp_list[:]:  # 拆分出项目，及对应用例
            project_and_cases = item.split("||")
            if len(project_and_cases) == 2:
                project_name = project_and_cases[0]
                cases_str = project_and_cases[1]

                cases_str_list = cases_str.split("|")  # 拆分用例

                cases_int_list = []
                # 拆分出用例
                for case in cases_str_list:
                    caseid_and_casename = case.split(":")  # 拆分出用例
                    cases_int_list.append(int(caseid_and_casename[0]))

                temp = [project_name, cases_int_list]

                self.global_cases.append(temp)
        return self.global_cases
