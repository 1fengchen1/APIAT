#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'shouke'

import unittest
import re
import json
import traceback,sys
from collections import OrderedDict

from globalpkg.log import logger
from globalpkg.global_var import  *
from interface.InterfaceUnittestTestCase import *
from interface.wecharno_card_coupon import *

class CaseStep:
    outputs_dict = {} # 专门用于存放从数据库服务器提取的值
    def __init__(self, step_id, step_number, expected_result, action, testcase_id):
        self.step_id = step_id
        self.expected_result= expected_result
        self.action = action
        self.step_number = step_number
        self.testcase_id = testcase_id

    def get_step_id(self):
        return self.step_id

    def get_expected_result(self):
        return self.expected_result

    def set_expected_result(self, expected_result):
        self.expected_result = expected_result

    def get_action(self):
        return  self.action

    def set_action(self, action):
        self.action = action

    def set_function_of_action(self,function):
        self.action['函数'] = function


    def set_method_of_action(self, method):
        self.action['方法'] = method

    def get_method_of_action(self):
        return  self.action['方法']

    def set_params_of_action(self, params):
        self.action['参数'] = params

    def get_params_of_action(self):
        return self.action['参数']

    def get_url_of_action(self):
        return self.action['url']

    def set_url_of_action(self, url):
        self.action['url'] = url

    def get_step_number(self):
        return  self.step_number

    def get_preconditions(self):
        return  self.get_preconditions

    def get_summary(self):
        return self.summary

    def get_tasecase_id(self):
        return  self.testcase_id

    # 接口请求参数中动态参数转换成具体的参数值
    def __repalce_value_of_parmas_in_quest(self, params):
        is_list_params = 0
        str_dic = '{"key":"value"}'
        temp_re = json.loads(str_dic, object_pairs_hook=OrderedDict)
        is_ordered_dict = 0

        if type([]) == type(params): # params为预期结果中的“条件”
            params = str(params).lstrip('[')
            params = params.rstrip(']')
            is_list_params = 1
        elif type(params) == type(temp_re):  # step_action为OrderdDict
            params = json.dumps(params)
            is_ordered_dict = 1

        if type(params) == type({}): # json串
            # 遍历查找动态参数
            for key, value in params.items():
                if type(value) == type(''): # 值为动态参数的前提
                    if value[0:1] == '[' and value[0:2] not in ('[@', '[{') and value[-1:] == ']' and value[1:8] != 'global_'and not value[1:-1].isdigit(): # 参数名不能为纯数字,[@、[{打头: # 非全局参数
                        logger.info('从json字典串中找到待替换的非全局动态参数：%s' % value)
                        value = value.lstrip('[')
                        value = value.rstrip(']')
                        if value.find('.') == -1:
                            class_name = 'InterfaceUnittestTestCase'
                            param_name = value
                        else:
                            class_name, param_name = value.split('.')
                        output_dict = (globals()[class_name]).outputs_dict

                        if param_name in output_dict.keys():
                            params[key] = output_dict[param_name]  # 替换参数

                    elif value[0:1] == '[' and value[-1:] == ']' and value[1:8] == 'global_': # 全局参数
                        logger.info('从json字典串中找到待替换的全局动态参数：%s' % value)
                        param_name = value.lstrip('[')
                        param_name = param_name.rstrip(']')

                        try:
                            params[key] = globals()[param_name]
                        except Exception as e:
                            logger.error('转换全局动态参数出错 %s' % e)

            logger.info('转换后的参数体为：%s' % params)
            return  params
        elif type(params) == type(''): # 字符串类型的参数
            # 遍历查找动态参数
            var_params = re.findall('\[.+?\]', params)
            if var_params == []:
                logger.info('没找到需要替换的动态参数')
                if is_ordered_dict == 1:
                    params = json.loads(params, object_pairs_hook=OrderedDict)
                elif is_list_params == 1:
                    params = '[' + params + ']'
                    params = eval(params)
                return params

            new_params = params
            for item in var_params:
                if item[1:8] != 'global_' and not item[1:-1].isdigit() and item[0:2] not in ('[@', '[{'): # 参数名不能为纯数字，不能以[@、[{打头
                    logger.info('从字符串中找到待替换的非全局动态参数：%s' % item)
                    value = item.lstrip('[')
                    value = value.rstrip(']')
                    if value.find('.') != -1:
                        class_name, param_name = value.split('.')
                    else:
                        class_name = 'InterfaceUnittestTestCase'
                        param_name = value
                    output_dict = (globals()[class_name]).outputs_dict

                    if param_name in output_dict.keys():
                        if type(output_dict[param_name]) != type(''): # 参数值不为字符串类型，"key":"[var]",转为"key":var
                             item = "'" + item + "'"
                        old_params =  new_params
                        new_params = new_params.replace(item, str(output_dict[param_name]))  # 替换参数
                        if new_params == old_params:# 说明参数类似这样的："参数":"([CaseStep.branch_id],)"
                              item = item.strip("'")
                              new_params = new_params.replace(item, str(output_dict[param_name]))  # 替换参数
                elif item[1:8] == 'global_':
                    logger.info('从字符串中找到待替换的全局动态参数：%s' % item)
                    param_name = item.lstrip('[')
                    param_name = param_name.rstrip(']')

                    try:
                        new_params = new_params.replace(item, str(globals()[param_name]))
                    except Exception as e:
                        logger.error('转换全局动态参数出错 %s' % e)

            if is_ordered_dict == 1:
                new_params = json.loads(new_params, object_pairs_hook=OrderedDict)				
            elif is_list_params == 1:
                new_params = '[' + new_params + ']'
                new_params = eval(new_params)
            logger.info('转换后的参数体为：%s' % new_params)
            return  new_params
        else:
            logger.info('没找到需要替换的动态参数')
            return  params

    def run_step(self, http=None):
        if  '步骤类型' in self.action and (self.action['步骤类型']).lower() == '执行sql':
            # 执行sql脚本
            step_run_result = self.run_sql_in_action()
            logger.debug('step_run_result：error, %s' % step_run_result[1])
            return  (step_run_result[0], [('CaseStep',step_run_result[1])])
        else:
            try:
                if '类名' in self.action.keys():
                    class_name = self.action['类名']
                else:
                    class_name = 'InterfaceUnittestTestCase'
                if '函数' in self.action.keys():
                    function = self.action['函数']
                else:
                    function = 'test_interface_of_urlencode'
                logger.info('调用的方法为：%s.%s' % (class_name, function))
            except Exception as e:
                logger.error('步骤[%s]信息填写不正确: %e，执行失败' % (self.step_number,e))
                return ('Error',[('CaseStep','%s' % e)])

            # 替换动态参数
            self.action['参数'] = self.__repalce_value_of_parmas_in_quest(self.action['参数'])
            self.action['url'] = self.__repalce_value_of_parmas_in_quest(self.action['url'])
            if self.expected_result != '' and '条件' in self.expected_result.keys():
                self.expected_result['条件'] = self.__repalce_value_of_parmas_in_quest(self.expected_result['条件'])
            if  '请求头' in self.action.keys():
                self.action['请求头'] = self.__repalce_value_of_parmas_in_quest(self.action['请求头'])
                self.action['请求头'] = json.dumps(self.action['请求头'])
                self.action['请求头'] = json.loads(self.action['请求头'])

            runner = unittest.TextTestRunner()
            test_step_action = unittest.TestSuite()
            test_step_action.addTest((globals()[class_name])(function, http, self))
            step_run_result = runner.run(test_step_action)

            logger.debug('step_run_result：%s, errors：%s，failures：%s' % (step_run_result, step_run_result.errors, step_run_result.failures))
            if 0 != len(step_run_result.errors):
                return ('Error', step_run_result.errors)
            elif 0 != len(step_run_result.failures):
                return ('Fail', step_run_result.failures)
            else:
                return ('Pass', '')

    # 执行sql
    def run_sql_in_action(self):
        if '单条查询' in self.action:
            self.action['参数'] =  self.__repalce_value_of_parmas_in_quest(self.action['参数'])
            if self.action['参数'] != '':
                self.action['参数'] = eval(self.action['参数']) # 字符串类型的元组转为元组
            if '数据库' not in self.action.keys():
                return ('Error', '用例步骤未填写"数据库"')
            try:
                query_result, flag = globals()[self.action['数据库']].select_one_record(self.action['单条查询'],self.action['参数'])
                logger.info('数据库服务器返回的查询结果为为 query_result:%s, flag:%s' % (query_result,flag))
                if flag == True:
                    logger.info('正在保存服务器返回结果到自定义变量')
                    if query_result:
                        self.save_onesql_query_result(query_result) # 保存查询记录
                    if self.expected_result and '条件' in self.expected_result.keys():
                        self.expected_result['条件'] = self.__repalce_value_of_parmas_in_quest(self.expected_result['条件'])
                        assert_result = self.assert_sql_result(self.expected_result['条件'])
                        if assert_result[0] == 'Fail':
                            return('Fail',assert_result[1])
                    return ('Pass','')
                else:
                    return ('Error',str(query_result))
            except Exception as e:
                return('Error', '%s' % e)
                
        elif '更新' in self.action:
            self.action['参数'] = self.__repalce_value_of_parmas_in_quest(self.action['参数'])
            self.action['参数'] = eval(self.action['参数'])
            if '数据库' not in self.action.keys():
                return ('Error', '用例步骤未填写"数据库"')
            try:
                query_result,flag = globals()[self.action['数据库']].execute_update(self.action['更新'],self.action['参数'])
                if flag == True:
                    return ('Pass','')
                else:
                    return ('Error',str(query_result))
            except Exception as e:
                return('Error', '%s' % e)

    # 保存从数据库服务器返回中的内容
    def save_onesql_query_result(self, sql_record):
        if self.expected_result and '输出' in self.expected_result.keys(): # 需要提取服务器返回内容
            output = self.expected_result['输出']

            counter = 0
            while counter < len(sql_record):
                for var_name, var_number in output.items():
                    var_number = int(var_number) #以防错误输入了字符串编号
                    temp_var_number = var_number - 1
                    if temp_var_number == counter:
                        CaseStep.outputs_dict[var_name] = sql_record[counter]# 已有存在值，替换已经存在的值
                        logger.debug('提取的输出结果(key-value对)为:%s-%s' % (var_name, sql_record[counter]))
                counter = counter + 1

            logger.debug('提取的输出结果(key-value对)为:%s' % CaseStep.outputs_dict)
        else:
            logger.warn('未检测到从数据库服务器返回中提取内容的要求，请检查是否正确填写预期结果')


    def assert_sql_result(self, response_to_check):
        if self.expected_result != '':
            if re.findall('匹配规则', str(self.expected_result)) == []:
                logger.info('用户没有设置匹配规则，返回程序')
                return ['Pass', '']
        traceback_template = '''Traceback (most recent call last):
             File "%(filename)s", line %(lineno)s, in %(name)s
             %(type)s: %(message)s\n'''
        if self.expected_result['匹配规则'] == '相等':
            # 遍历条件列表， 形如 "条件"：[{"模式"："[CaseStep.device_no]=true", "消息"：“登录失败，success不为true”},{"模式"："[CaseStep.serial_no]=\ "成功\"","消息"：“message不为成功”}，
            # {"模式"："[CaseStep.serial_no]= "[CaseStep.branch_id]"},"消息"：“code不为4001”},{"模式"："\"[CaseStep.branch_id]\"= "\"[CaseStep.branch_id]\""},"消息"：“code不为4002”}],
            for item in self.expected_result['条件']:
                member = item['模式']
                logger.info('要检测的模式为：%s' % member)

                value_list = member.split('=')
                if len(value_list) < 2:
                    logger.warn('该条件模式[%s]填写错误，跳过对该模式的检测' % member)
                    break
                msg = item['消息']
                try:
                    assert value_list[0] == value_list[1], msg
                except AssertionError:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback_details = {
                        'filename': exc_traceback.tb_frame.f_code.co_filename,
                        'lineno' : exc_traceback.tb_lineno,
                        'name'  : exc_traceback.tb_frame.f_code.co_name,
                        'type'  : exc_type.__name__,
                        'message' : exc_value
                    }
                    del(exc_type, exc_value, exc_traceback)
                    traceback_exc = traceback_template % traceback_details
                    return ['Fail', traceback_exc]
            return ['Pass', '']
        elif self.expected_result['匹配规则'] == '不相等':
            for item in self.expected_result['条件']:
                member = item['模式']
                member = member.replace('！=', '!=') # 防止用户输入中文的！
                logger.info('要检测的模式为：%s' % member)
                value_list = member.split('!=')
                if len(value_list) < 2:
                    logger.warn('该条件模式[%s]填写错误，跳过对该模式的检测' % member)
                    break
                msg = item['消息']
                try:
                    assert value_list[0] != value_list[1], msg
                except AssertionError:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback_details = {
                        'filename': exc_traceback.tb_frame.f_code.co_filename,
                        'lineno' : exc_traceback.tb_lineno,
                        'name'  : exc_traceback.tb_frame.f_code.co_name,
                        'type'  : exc_type.__name__,
                        'message' : exc_value
                    }
                    del(exc_type, exc_value, exc_traceback)
                    traceback_exc = traceback_template % traceback_details
                    return ['Fail', traceback_exc]
            return ['Pass', '']
        else:
            logger.warn('匹配规则填写错误["匹配规则"："%s"]' % self.expected_result['匹配规则'])
            return ['Fail', '匹配规则填写错误["匹配规则"："%s"]，匹配规则可选择值 相等|不相等' % self.expected_result['匹配规则']]
