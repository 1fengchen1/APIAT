#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'shouke'

import unittest
import json
import re
import xml.etree.ElementTree as ET

from globalpkg.log import logger
from globalpkg.global_var import other_tools


class MyUnittestTestCase(unittest.TestCase):

    def __init__(self, methodName='runTest', http=None, casestep=None):
        super(MyUnittestTestCase, self).__init__(methodName)
        self.http = http
        if '请求头' in casestep.get_action().keys():
            self.headers = casestep.get_action()['请求头']
        else:
            self.headers = {}
        self.method = casestep.get_action()['方法']
        self.url = casestep.get_action()['url']
        self.params = casestep.get_action()['参数']
        self.testcase_id = casestep.get_tasecase_id()
        self.step_id = casestep.get_step_id()
        self.expected_result = casestep.get_expected_result()
        self.casestep = casestep

    # 断言
    def assert_result(self, response_to_check):
        '''
        执行预期结果
        :param response_to_check: 服务器返回的响应
        :return: 用户没有设置匹配规则，返回程序
        '''
        if self.expected_result != '':
            if re.findall('匹配规则', str(self.expected_result)) == []:
                logger.info('用户没有设置匹配规则，返回程序')
                self.assertEqual(1, 1, msg='用户没有设置匹配规则')
                return

        if self.expected_result != '':
            if self.expected_result['匹配规则'] == '包含成员':
                if type(response_to_check) not in [type(''), type([]), type(()), type(set()), type({})]:
                    logger.error('服务器返回内容为不可迭代对象')
                    self.assertEqual(1, 0, msg='服务器返回内容为不可迭代对象')

                # 遍历条件列表， 形如 "条件":[{"模式":"\"success\"", "消息":"创建储值卡支付订单失败,返回json串不包含key - success"},{"模式":"\"attach\"", "消息":"创建储值卡支付订单失败,返回json串不包含key - attach"}]
                for item in self.expected_result['条件']:
                    member = item['模式']
                    logger.info('要匹配的模式（成员）为：%s' % member)
                    self.assertIn(member, response_to_check, msg=item['消息'])

            elif self.expected_result['匹配规则'] == '不包含成员':
                if type(response_to_check) not in [type(''), type([]), type(()), type(set()), type({})]:
                    logger.error('服务器返回内容为不可迭代对象')
                    self.assertEqual(1, 0, msg='服务器返回内容为不可迭代对象')

                # 遍历条件列表，形如 "条件":[{"模式":"\"success\"", "消息":"创建储值卡支付订单失败,返回json串包含key - success"},{"模式":"\"attach\"", "消息":"创建储值卡支付订单失败,返回json串包含key - attach"}]
                for item in self.expected_result['条件']:
                    member = item['模式']
                    logger.info('要匹配的模式（成员）为：%s' % member)
                    self.assertNotIn(member, response_to_check, msg=item['消息'])

            elif self.expected_result['匹配规则'] == '包含字符串':
                if type(response_to_check) in [type({}), type(set()), type(()), type([]), type(1), type(0.01)]:
                    response_to_check = str(response_to_check)
                elif type(response_to_check) != type(''):
                    logger.error('服务器返回内容不为字符串类型')
                    self.assertEqual(1, 0, msg='服务器返回内容不为字符串类型')

                # 遍历条件列表, 形如："条件":[{"模式":"\"success\":true", "消息":"创建储值卡支付订单失败，success不为True"},{"模式":"\"success\":false", "消息":"创建储值卡支付订单失败，success不为false"}]
                for item in self.expected_result['条件']:
                    pattern_str = item['模式']
                    logger.info('要匹配的模式（子字符串）为：%s' % pattern_str)
                    self.assertIn(pattern_str, response_to_check, item['消息'])

            elif self.expected_result['匹配规则'] == '不包含字符串':
                if type(response_to_check) in [type({}), type(set()), type(()), type([]), type(1), type(0.01)]:
                    response_to_check = str(response_to_check)
                elif type(response_to_check) != type(''):
                    logger.error('服务器返回内容不为字符串类型')
                    self.assertEqual(1, 0, msg='服务器返回内容不为字符串类型')

                # 遍历条件列表, 形如："条件":[{"模式":"\"success\":true", "消息":"创建储值卡支付订单失败，success不为True"},{"模式":"\"success\":false", "消息":"创建储值卡支付订单失败，success不为false"}]
                for item in self.expected_result['条件']:
                    pattern_str = item['模式']
                    logger.info('要匹配的模式（子字符串）为：%s' % pattern_str)
                    self.assertNotIn(pattern_str, response_to_check, item['消息'])

            elif self.expected_result['匹配规则'] == '键值相等':
                if type(response_to_check) == type(''):  # 字符串类型的字典、json串
                    try:
                        response_to_check = json.loads(response_to_check)  # //转字符串为json
                    except Exception as e:
                        logger.error('转换服务器返回内容为字典失败')
                        self.assertEqual(1, 0, msg='转换服务器返回内容为字典失败')

                if type(response_to_check) == type([]):  # 格式[{}]的json串
                    try:
                        response_to_check = response_to_check[0]
                        response_to_check = json.loads(response_to_check)  # //转字符串为json
                    except Exception as e:
                        logger.error('转换服务器返回内容为字典失败')
                        self.assertEqual(1, 0, msg='转换服务器返回内容为字典失败')

                if type(response_to_check) != type({}):
                    logger.error('服务器返回内容不为字典、字符串类型的字典')
                    self.assertEqual(1, 0, msg='服务器返回内容不为字典、字符串类型的字典')

                # 遍历条件列表, 形如："条件":[{"模式":{"success":true}, "消息":"创建储值卡支付订单失败，success不为True"},{"模式":{"success":false}, "消息":"创建储值卡支付订单失败，success不为false"}]
                for item in self.expected_result['条件']:
                    pattern_dic = item['模式']
                    # 获取list方式标识的key,value层级值
                    dict_level_list = other_tools.get_dict_level_list(pattern_dic)
                    other_tools.set_dict_level_list([])
                    logger.info('要匹配的字典key,value层级为：%s' % dict_level_list)

                    last_value = other_tools.find_dict_last_leve_value(dict_level_list, response_to_check)
                    logger.info('找到的对应字典层级的最后值为：%s' % last_value)
                    other_tools.set_key_index(0)

                    # 比较同层级，相同key对应的value值
                    self.assertEqual(dict_level_list[len(dict_level_list) - 1], last_value, item['消息'])

            elif self.expected_result['匹配规则'] == '匹配正则表达式':
                if type(response_to_check) in [type({}), type(set()), type(()), type([]), type(1), type(0.01)]:
                    response_to_check = str(response_to_check)
                elif type(response_to_check) != type(''):
                    logger.error('服务器返回内容不为字符串类型')
                    self.assertEqual(1, 0, msg='服务器返回内容不为字符串类型')

                # 遍历条件列表, 形如( "条件":[{"模式":"\"success\":true", "消息":"创建储值卡支付订单失败，success不为True"},{"模式":"\"success\":false", "消息":"创建储值卡支付订单失败，success不为false"}]
                for item in self.expected_result['条件']:
                    pattern_str = item['模式']

                    logger.info('要匹配的模式（正则表达式）为：%s' % pattern_str)
                    self.assertRegex(response_to_check, pattern_str, msg=item['消息'])

            elif self.expected_result['匹配规则'] == '不匹配正则表达式':
                if type(response_to_check) in [type({}), type(set()), type(()), type([]), type(1), type(0.01)]:
                    response_to_check = str(response_to_check)
                elif type(response_to_check) != type(''):
                    logger.error('服务器返回内容不为字符串类型')
                    self.assertEqual(1, 0, msg='服务器返回内容不为字符串类型')

                # 遍历条件列表，形如  "条件":[{"模式":"\"success\":true", "消息":"创建储值卡支付订单失败，success为True"},{"模式":"\"success\":false", "消息":"创建储值卡支付订单失败，success为false"}]
                for item in self.expected_result['条件']:
                    pattern_str = item['模式']

                    logger.info('要匹配的模式（正则表达式）为：%s' % pattern_str)
                    self.assertNotRegex(response_to_check, pattern_str, msg=item['消息'])

            elif self.expected_result['匹配规则'] == '完全匹配字典':
                if type(response_to_check) == type(''):  # 字符串类型的字典、json串
                    try:
                        response_to_check = json.loads(response_to_check)  # //转字符串为json
                    except Exception as e:
                        logger.info('转换服务器返回内容为字典失败')
                        self.assertEqual(1, 0, msg='转换服务器返回内容为字典失败')
                elif type(response_to_check) != type({}):
                    logger.error('服务器返回内容不为字典')
                    self.assertEqual(1, 0, msg='服务器返回内容不为字典')

                # 遍历条件列表 "条件":[{"模式":{"success":true}, "消息":"创建储值卡支付订单失败,返回结果和字典模式不匹配"}]
                for item in self.expected_result['条件']:
                    pattern_dic = item['模式']

                    logger.info('要匹配的模式（字典）为：%s' % pattern_dic)
                    self.assertDictEqual(response_to_check, pattern_dic, msg=item['消息'])

            elif self.expected_result['匹配规则'] == '完全匹配列表':
                if type(response_to_check) == type(''):  # 字符串类型的列表
                    try:
                        response_to_check = eval(response_to_check)
                    except Exception as e:
                        logger.info('转换服务器返回内容为列表失败')
                        self.assertEqual(1, 0, msg='转换服务器返回内容为列表失败')

                if type(response_to_check) != type([]):
                    logger.info('服务器返回内容不为列表或列表的字符串表示')
                    self.assertEqual(1, 0, msg='服务器返回内容不为列表或列表的字符串表示')

                # 遍历条件列表，形如 "条件":[{"模式":"[\"success\",\"shouke\",2016]", "消息":"创建储值卡支付订单失败,返回结果和列表模式不匹配"}]
                for item in self.expected_result['条件']:
                    pattern_list = eval(item['模式'])

                    logger.info('要匹配的模式（列表）为：%s' % pattern_list)
                    self.assertListEqual(response_to_check, pattern_list, msg=item['消息'])

            elif self.expected_result['匹配规则'] == '完全匹配集合':
                if type(response_to_check) == type(''):  # 字符串类型的集合
                    try:
                        response_to_check = eval(response_to_check)
                    except Exception as e:
                        logger.error('转换服务器返回内容为集合失败')
                        self.assertEqual(1, 0, msg='转换服务器返回内容为集合失败')

                if type(response_to_check) != type(set()):
                    logger.error('服务器返回内容不为集合或集合的字符串表示')
                    self.assertEqual(1, 0, msg='服务器返回内容不为集合或集合的字符串表示')

                # 遍历条件列表,形如 "条件":[{"模式":"[\"success\",\"shouke\",2016]", "消息":"创建储值卡支付订单失败,返回结果和列表模式不匹配"}]
                for item in self.expected_result['条件']:
                    pattern_set = eval(item['模式'])

                    logger.info('要匹配的模式（集合）为：%s' % pattern_set)
                    self.assertSetEqual(response_to_check, pattern_set, msg=item['消息'])

            elif self.expected_result['匹配规则'] == '完全匹配元组':
                if type(response_to_check) == type(''):  # 字符串类型的元组
                    try:
                        response_to_check = eval(response_to_check)
                    except Exception as e:
                        logger.error('转换服务器返回内容为元组失败')
                        self.assertEqual(1, 0, msg='转换服务器返回内容为元组失败')

                if type(response_to_check) != type(()):
                    logger.error('服务器返回内容不为元组或元组的字符串表示')
                    self.assertEqual(1, 0, msg='服务器返回内容不为元组或元组的字符串表示')

                # 遍历条件列表,形如 "条件":[{"模式":"[\"success\",\"shouke\",2016]", "消息":"创建储值卡支付订单失败,返回结果和列表模式不匹配"}]
                for item in self.expected_result['条件']:
                    pattern_tuple = eval(item['模式'])

                    logger.info('要匹配的模式（元组）为：%s' % str(pattern_tuple))
                    self.assertTupleEqual(response_to_check, pattern_tuple, msg=item['消息'])

            elif (self.expected_result['匹配规则']).lower() == 'xpath断言':
                try:
                    root = ET.fromstring(response_to_check)
                except ET.ParseError as e:
                    self.assertEqual(1, 0, '%s' % e)

                for item in self.expected_result['条件']:
                    pattern_dic = item['模式']
                    logger.info('要检测的模式为：%s' % pattern_dic)
                    for key in pattern_dic.keys():
                        if key == '.':
                            content_to_check = root.text
                            expect_value = pattern_dic[key]
                        else:
                            xmlnsnamespace_dic = {}  # 存放 前缀:对应uri
                            logger.info('正在获取xmlns定义')
                            match_result_list = re.findall('xmlns[^:]?=(.+?)[ |\>|\\\>]', response_to_check,
                                                           re.MULTILINE)
                            if match_result_list:
                                xmlns = match_result_list[len(match_result_list) - 1]
                                xmlns = xmlns.strip(' ')
                                xmlns = '{' + xmlns + '}'
                                logger.info('xmlns定义为：%s' % xmlns)
                                xmlnsnamespace_dic['xmlns'] = xmlns

                            logger.info('正在获取"xmlns:xxx名称空间定义')
                            match_result_list = re.findall('xmlns:(.+?)=(.+?)[ |>]', response_to_check)
                            for ns in match_result_list:
                                xmlnsnamespace_dic[ns[0]] = '{' + ns[1] + '}'

                            logger.info("最后获取的prefix:uri为：%s" % xmlnsnamespace_dic)

                            logger.info('正在转换元素结点前缀')
                            key_copy = key
                            for dic_key in xmlnsnamespace_dic.keys():
                                namespace = dic_key + ':'
                                if namespace in key:
                                    uri = xmlnsnamespace_dic[dic_key]
                                    key = key.replace(namespace, uri)
                                    key = key.replace('"', '')

                            logger.info('转换后用于查找元素的xpath：%s' % key)
                            try:
                                elements_list = root.findall(key)
                            except Exception as e:
                                logger.error('查找元素出错：%s' % e)
                                self.assertEqual(1, 0, msg='%s' % e)
                            logger.info('查找到的元素为：%s' % elements_list)

                            logger.info('正在进行断言')
                            if elements_list:
                                content_to_check = elements_list[0].text
                            else:
                                content_to_check = ''
                            expect_value = pattern_dic[key_copy]
                        logger.info('从服务器返回的提取的待检查数据的类型：%s' % type(content_to_check))
                        logger.info('用户期望值的数据类型：%s' % type(expect_value))
                        self.assertEqual(content_to_check, expect_value, msg=item['消息'])

    # 提取服务器返回内容
    def extrator(self, extrator_type, extrator, response_to_check=''):
        if extrator_type == 'dic':  # 获取键值
            #  获取list方式标识的key,value层级值
            dict_level_list = other_tools.get_dict_level_list(extrator)
            other_tools.set_dict_level_list([])

            logger.info('要提取的字典key,value层级为：%s' % dict_level_list)

            if type(response_to_check) == type(''):  # 字符串类型的字典、json串
                try:
                    response_to_check = json.loads(response_to_check)  # //转字符串为json
                except Exception as e:
                    logger.error('转换服务器返回内容为字典失败：%s' % e)
                    return ''

            if type(response_to_check) != type({}):
                logger.error('服务器返回内容不为字典、字符串类型的字典')
                return ''

            value_get = other_tools.find_dict_last_leve_value(dict_level_list, response_to_check)
            logger.info('找到的对应字典层级的key的值为：%s' % value_get)
            other_tools.set_key_index(0)

            return value_get
        elif extrator_type == 're':  # 获取正则表达式匹配的内容
            if type(response_to_check) in [type({}), type(set()), type(()), type([]), type(1), type(0.01)]:
                response_to_check = str(response_to_check)
            elif type(response_to_check) != type(''):
                logger.error('服务器返回内容不为字符串类型')
                return []
            result = re.findall(extrator, response_to_check)
            return result
        elif extrator_type == 'xpath':
            try:
                root = ET.fromstring(response_to_check)
            except ET.ParseError as e:
                logger.error('%s' % e)
                return ''

            logger.info('xpath表达式为：%s' % extrator)
            if extrator == '.':
                value_get = root.text
            else:
                xmlnsnamespace_dic = {}  # 存放 前缀:对应uri
                logger.info('正在获取xmlns定义')
                match_result_list = re.findall('xmlns[^:]?=(.+?)[ |\>|\\\>]', response_to_check, re.MULTILINE)
                if match_result_list:
                    xmlns = match_result_list[len(match_result_list) - 1]
                    xmlns = xmlns.lstrip(' ')
                    xmlns = '{' + xmlns + '}'
                    logger.info('xmlns定义为：%s' % xmlns)
                    xmlnsnamespace_dic['xmlns'] = xmlns

                    logger.info('正在获取"xmlns:xxx名称空间定义')
                    match_result_list = re.findall('xmlns:(.+?)=(.+?)[ |>]', response_to_check)
                    for ns in match_result_list:
                        xmlnsnamespace_dic[ns[0]] = '{' + ns[1] + '}'

                    logger.info("最后获取的prefix:uri为：%s" % xmlnsnamespace_dic)

                    logger.info('正在转换元素结点前缀')
                    for dic_key in xmlnsnamespace_dic.keys():
                        namespace = dic_key + ':'
                        if namespace in extrator:
                            uri = xmlnsnamespace_dic[dic_key]
                            extrator = extrator.replace(namespace, uri)
                            extrator = extrator.replace('"', '')

                    logger.info('转换后用于查找元素的xpath：%s' % extrator)

                    try:
                        elements_list = root.findall(extrator)
                    except Exception as e:
                        logger.error('查找xpath元素出错:%s' % e)
                        value_get = ''
                    logger.info('查找到的元素为：%s' % elements_list)
                    if elements_list:
                        value_get = elements_list[0].text
                    else:
                        value_get = ''
            return value_get
        else:
            logger.error('提取器填写错误')
            return None

    # 保存从服务器返回中提取的内容
    def save_result(self, response_to_check):
        if '输出' in self.expected_result.keys():  # 需要提取服务器返回内容
            output = self.expected_result['输出']

            if type(output) == type({}):
                for key in output.keys():

                    if key.lower() == 'dic':  # 如果为字典,则用键值提取
                        for var_name, extrator in output[key].items():
                            logger.info('使用键值提取')
                            value_get = self.extrator('dic', extrator, response_to_check)  # 获取键对应值
                            logger.info('获取到的变量的值为：%s' % value_get)

                            self.outputs_dict[var_name] = value_get
                            logger.info(
                                '使用“键值提取”提取的自定义变量-值(key-value对)为:%s-%s' % (var_name, self.outputs_dict[var_name]))

                    elif key.lower() == 're':
                        for var_name, extrator in output[key].items():
                            logger.info('使用正则表达式提取')
                            value_get = self.extrator('re', extrator, response_to_check)

                            index = 1
                            tmp_var_name = var_name
                            for item in value_get:
                                logger.info('获取到的变量的值为：%s' % value_get)

                                var_name = var_name + '_' + str(index)
                                if var_name in self.outputs_dict.keys():  # 已有存在值，替换已经存在的值
                                    self.outputs_dict[var_name] = item
                                    continue
                                else:
                                    self.outputs_dict[var_name] = item
                                    index = index + 1
                                logger.info('使用“正则表达式提取”提取的自定义变量-值(key-value对)为:%s-%s' % (
                                    var_name, self.outputs_dict[var_name]))
                                var_name = tmp_var_name

                    elif key.lower() == 'xpath':
                        for var_name, extrator in output[key].items():
                            logger.info('使用xpath提取')
                            value_get = self.extrator('xpath', extrator, response_to_check)
                            logger.info('获取到的变量的值为：%s' % value_get)

                            self.outputs_dict[var_name] = value_get
                            logger.info(
                                '使用“xpath提取”提取的自定义变量-值(key-value对)为:%s-%s' % (var_name, self.outputs_dict[var_name]))

                logger.debug('提取的变量-值(key-value对)为:%s' % self.outputs_dict)
        else:
            logger.warn('未检测到从服务器返回中提取内容的要求，请检查是否正确填写预期结果')

    def tearDown(self):
        pass
