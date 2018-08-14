#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = '1fengchen1'
__QQ__ = '758896823'

import os

from pyh import *
from globalpkg.log import logger
from globalpkg.global_var import testdb
from globalpkg.global_var import testcase_report_tb
from globalpkg.global_var import executed_history_id
from globalpkg.global_var import other_tools


class HtmlReport:
    def __init__(self, title, head):
        self.title = title  # 网页标签名称
        self.head = head  # 标题
        self.filename = 'testrepot.html'  # 结果文件名
        self.dir = './testreport/'  # 结果文件目录
        self.time_took = '00:00:00'  # 测试耗时
        self.success_num = 0  # 测试通过的用例数
        self.fail_num = 0  # 测试失败的用例数
        self.error_num = 0  # 运行出错的用例数
        self.block_num = 0  # 未运行的测试用例总数
        self.case_total = 0  # 运行测试用例总数

    # 生成HTML报告
    def generate_html(self, file):
        page = PyH(self.title)
        page.addCSS("../static/css/bootstrap.min.css")
        page.addJS("../static/js/textover.js")
        Container = page << body(id='Body', cl='bg-warning') << div(id="container",cl="container")

        # 报告标题 start
        Headrow = Container << div(id="Headrow", cl="row")
        Headrow << h1(id="HeadH1",align="center") << strong(self.head, id="HeadTxt") + small("Sonny.zhang", id="author")
        Headrow << br()
        # 报告标题 end

        # 数据统计展示 start
        Totalrow = Container << div(id="Totalrow", cl="Totalrow") << div(cl="jumbotron")
        # --测试使用时间，测试用例总数--
        UTimerow = Totalrow << div(id="UTimerow", cl="row")
        UTimerow << div(cl="col-xs-12 col-md-6") << p(role="presentation") << span("测试总耗时：") << span(self.time_took, cl="label label-default")

        # 查询数据 start
        logger.info('正在查询测试用例总数')
        query = 'SELECT count(testcase_id) FROM ' + testcase_report_tb + ' WHERE executed_history_id = %s'
        data = (executed_history_id,)
        result = testdb.select_one_record(query, data)
        self.case_total = result[0][0]

        logger.info('正在查询执行通过的用例数')
        query = 'SELECT count(testcase_id) FROM ' + testcase_report_tb + ' WHERE runresult = %s AND executed_history_id = %s'
        data = ('Pass', executed_history_id)
        result = testdb.select_one_record(query, data)
        self.success_num = result[0][0]

        logger.info('正在查询执行失败的用例数')
        query = 'SELECT count(testcase_id) FROM ' + testcase_report_tb + ' WHERE runresult = %s AND executed_history_id = %s'
        data = ('Fail', executed_history_id)
        result = testdb.select_one_record(query, data)
        self.fail_num = result[0][0]

        logger.info('正在查询执行出错的用例数')
        query = 'SELECT count(testcase_id) FROM ' + testcase_report_tb + ' WHERE runresult = %s AND executed_history_id = %s'
        data = ('Error', executed_history_id)
        result = testdb.select_one_record(query, data)
        self.error_num = result[0][0]

        logger.info('正在查询未执行的用例数')
        query = 'SELECT count(testcase_id) FROM ' + testcase_report_tb + ' WHERE runresult = %s AND executed_history_id = %s'
        data = ('Block', executed_history_id)
        result = testdb.select_one_record(query, data)
        self.block_num = result[0][0]

        # 查询数据 end

        UTimerow << div(cl="col-xs-12 col-md-6") << p(role="presentation") << span("用例总数：") \
                    << span(str(self.case_total), cl="label label-primary")

        # --用例失败成功统计--
        Amountrow = Totalrow << div(id="Amountrow", cl="row")
        Num1 = Amountrow << div(id="Num1", cl="col-xs-12 col-md-3") << p(role="presentation") << span() \
               << small("成功用例数(Pass)：") << span(str(self.success_num), cl="label label-success")
        Num2 = Amountrow << div(id="Num2", cl="col-xs-12 col-md-3") << p(role="presentation") << span() \
               << small("失败用例数(Fail)：") << span(self.fail_num, cl="label label-danger")
        Num3 = Amountrow << div(id="Num3", cl="col-xs-12 col-md-3") << p(role="presentation") << span() \
               << small("出错用例数(Error)：") << span(self.error_num, cl="label label-warning")
        Num4 = Amountrow << div(id="Num4", cl="col-xs-12 col-md-3") << p(role="presentation") << span() \
               << small("未执行用例数(Block)：") << span(self.block_num, cl="label label-default")
        # 数据统计 end

        # 测试计划 start
        Plans = Container << div(id="plans", cl="row")
        # --栏目标题--
        plans_title = "测试用例摘要"
        PlansTitle = Plans << div(id="plans-title", cl="panel panel-primary") << div(cl="panel-heading") \
                     << strong() << center(plans_title, cl="text-uppercase")

        
        # !--测试计划数据-- start
        logger.info('正在查询已运的测试计划')
        query = ('SELECT project, testplan FROM ' + testcase_report_tb + \
                 ' WHERE executed_history_id = %s GROUP BY project, testplan ORDER BY id ASC')
        data = (executed_history_id,)
        result = testdb.select_many_record(query, data)
        # !--测试计划数据-- end
        
        for row in result:
            # !--一个测试计划-- start
            Plan1 = Plans << div() << table(cl="table table-striped  bg-success")
            project = row[0]
            testplan = row[1]
            # ---一个标题--
            plan1_title = '测试计划【项目名称：' + project + ', 计划名称：<a name=\"first' + testplan + '\"' \
                          + 'href=\"#second' + testplan + '\">'+ testplan + '</a>】'
            Plan1 << center() << caption(plan1_title)

            # --一个列表--
            # ！--表头 start
            thead1 = ["ID", "执行编号", "用例ID", "用例外部ID", "用例名称", "用例套件", "执行结果", "运行时间"]
            Thead1 = Plan1 << thead()
            Thead1 << tr() << th(thead1[0]) \
                            + th(thead1[1]) \
                            + th(thead1[2]) \
                            + th(thead1[3]) \
                            + th(thead1[4]) \
                            + th(thead1[5]) \
                            + th(thead1[6]) \
                            + th(thead1[7])
            # ！--表头 end
            # ！--表体 start
            Tbody1 = Plan1 << tbody()
            logger.info('正在查询测试计划[project：%s, testplan：%s]的测试用例执行结果' % (row[0], row[1]))
            # 查询数据 start
            query = ('SELECT id, executed_history_id, testcase_id,tc_external_id, testcase_name,'
                     'testsuit, runresult, runtime FROM ' + testcase_report_tb + \
                     ' WHERE project=%s AND testplan=%s AND executed_history_id = %s GROUP BY testcase_id, runtime ORDER BY id ASC')
            data = (project, testplan, executed_history_id)
            result = testdb.select_many_record(query, data)
            # 查询数据 end
            
            logger.info('正在记录测试测试计划[project：%s, testplan：%s]的测试用例运行结果到测试报告' % (row[0], row[1]))
            for row in result:
                if row[6] != 'Pass':
                    td6 = td(p(row[6], cl="label label-danger  textover"))
                else:
                    td6 = td(row[6], cl="textover")
                Tbody1 << tr() << th(str(row[0]), scope="row") \
                                + td(row[1], cl="textover") \
                                + td(row[2], cl="textover") \
                                + td('<a name=\"first' + str(row[3]) + project + testplan + '\"' + 'href=\"#second' \
                                     + str(row[3]) + project + testplan + '\">' + row[3] + '</a>', cl="textover") \
                                + td(row[4], cl="textover") \
                                + td(row[5], cl="textover") \
                                + td6 \
                                + td(row[7], cl="textover")
            #！--表体 end
        # 测试计划 end
        

        # 测试用例 start
        Cases = Container << div(cl="row")
        # --栏目标题--
        cases_title = "用例执行明细"
        CasesTitle = Cases << div(cl="panel panel-primary") << div(cl="panel-heading") << strong(center(cases_title, cl="text-uppercase"))
        
        # ！--数据查询  start
        logger.info('正在查询已运的测试计划')
        query = ('SELECT project, testplan FROM ' + testcase_report_tb + \
                 ' WHERE executed_history_id = %s GROUP BY project, testplan ORDER BY id ASC')
        data = (executed_history_id,)
        result = testdb.select_many_record(query, data)
        # ！--数据查询  end

        # 遍历测试计划个数
        for row in result:
            project = row[0]
            testplan = row[1]
            # 一个测试计划 start
            Case1 = Cases << div(cl="col-xs-12 col-md-12") << table(cl="table table-striped  bg-success")
            # !--一个计划标题
            Cplan_title = '测试计划【项目名称：' + project + ', 计划名称：<a name=\"second' + testplan + '\"' + \
                          'href=\"#first' + testplan + '\">' + testplan + '</a>】'
            CplanTitle = Cases << center() << div(cl="panel panel-danger", style="width:1000px") \
                         << div(cl="panel-heading") << strong(center(Cplan_title, cl="text-uppercase"))
            
            # ！--数据查询  start
            logger.info('正在查询测试计划[project：%s, testplan：%s]已运行的测试用例' % (project, testplan))
            query = (
                        'SELECT tc_external_id, testcase_name, project, testplan, case_exec_history_id, testcase_id FROM ' + testcase_report_tb + \
                        ' WHERE project=%s AND testplan=%s AND executed_history_id = %s ' \
                        ' GROUP BY testcase_id,runtime ORDER BY id ASC')
            data = (project, testplan, executed_history_id)
            result = testdb.select_many_record(query, data)
            # ！--数据查询  end
            
            # 遍历测试用例的测试步骤执行结果
            for row in result:
                tc_external_id = row[0]
                case_name = row[1]
                project = row[2]
                testplan = row[3]
                case_exec_history_id = row[4]
                case_id = row[5]
                # 一个测试用例 start
                Case1 = Cases << div() << table(cl="table table-striped  bg-success")
                # !--一个用例标题
                case1_title = '测试用例【用例外部ID：' + tc_external_id + '，名称：<a name=\"second' + tc_external_id + project + testplan + '\"' + \
                    'href=\"#first' + tc_external_id + project + testplan + '\">' + case_name + '</a>】'
                Case1 << center() << caption(case1_title)
                # !--表头
                thead1 = ["步序", "协议方法", "协议", "主机", "端口", "ACTION", "预期结果", "运行结果", "原因分析", "运行时间"]
                Case1Thead1 = Case1 << thead()
                Case1Thead1 << tr() << th(thead1[0]) \
                                    + th(thead1[1]) \
                                    + th(thead1[2]) \
                                    + th(thead1[3]) \
                                    + th(thead1[4]) \
                                    + th(thead1[5]) \
                                    + th(thead1[6]) \
                                    + th(thead1[7]) \
                                    + th(thead1[8]) \
                                    + th(thead1[9])

                # !--表体
                Case1Tbody1 = Case1 << tbody()
                # ！--数据查询 start
                logger.info('正在查询测试用例[id=%s]步骤运行结果' % case_id)
                query = 'SELECT step_num, protocol_method, protocol, HOST, PORT, step_action, expected_results, runresult, reason, runtime ' \
                        'FROM case_step_report_tb ' \
                        'WHERE project= %s AND testplan= %s AND testcase_id = %s ' \
                        'AND executed_history_id = %s' \
                        'GROUP BY step_num ' \
                        'ORDER BY step_num ASC'
                data = (project, testplan, case_id, case_exec_history_id)
                result = testdb.select_many_record(query, data)
                # ！--数据查询 end
                for row in result:
                    if row[7] != 'Pass':
                        td7 = td(p(row[7], cl="label label-danger"))
                    else:
                        td7 = td(row[7])

                    Case1Tbody1 << tr() << th(str(row[0]), scope="row") \
                                        + td(row[1]) \
                                        + td(row[2]) \
                                        + td(row[3]) \
                                        + td(row[4]) \
                                        + td(str(row[5])) \
                                        + td(row[6])\
                                        + td7 \
                                        + td(row[8]) \
                                        + td(row[9])
          
                # 一个测试用例 end
        # 测试用例 end
        

        logger.info('正在设置测试报告结果文件名')
        self.__set_result_filename(file)

        logger.info('正在生成测试报告')
        page.printOut(self.filename)

    # 设置结果文件名
    def __set_result_filename(self, filename):
        parent_path, ext = os.path.splitext(filename)
        self.filename = self.dir + parent_path + str(executed_history_id) + ext
        logger.info('测试报告文件名所在路径为：%s' % self.filename)

    # 创建报告保存目录
    def mkdir_of_report(self, path):
        other_tools.mkdirs_once_many(path)
        self.dir = path

    def get_filename(self):
        return self.filename

    # 统计运行耗时
    def set_time_took(self, time):
        self.time_took = time
        return self.time_took
