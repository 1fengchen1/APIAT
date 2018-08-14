#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'shouke'

import configparser
import sys
import mysql.connector
from globalpkg.global_var import logger


class MyDB:
    """动作类，获取数据库连接，配置数据库IP，端口等信息，获取数据库连接"""

    def __init__(self, config_file, db):
        config = configparser.ConfigParser()

        # 从配置文件中读取数据库服务器IP、域名，端口
        config.read(config_file, encoding='utf-8')
        self.host = config[db]['host']
        self.port = config[db]['port']
        self.user = config[db]['user']
        self.passwd = config[db]['passwd']
        self.db_name = config[db]['db']
        self.charset = config[db]['charset']

        try:
            self.dbconn = mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.passwd,
                                                  database=self.db_name, charset=self.charset)
        except Exception as e:
            logger.error('初始化数据连接失败：%s' % e)
            sys.exit()

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_conn(self):
        return self.dbconn

    def execute_create(self, query):
        logger.info('query：%s' % query)
        try:
            db_cursor = self.dbconn.cursor()
            db_cursor.execute(query)
            db_cursor.execute('commit')
            db_cursor.close()
            return True
        except Exception as e:
            logger.error('创建数据库表操作失败：%s' % e)
            db_cursor.execute('rollback')
            db_cursor.close()
            exit()

    def execute_insert(self, query, data):
        logger.info('query：%s  data：%s' % (query, data))
        try:
            db_cursor = self.dbconn.cursor()
            db_cursor.execute(query, data)
            db_cursor.execute('commit')
            db_cursor.close()
            return True
        except Exception as e:
            logger.error('执行数据库插入操作失败：%s' % e)
            db_cursor.execute('rollback')
            db_cursor.close()
            exit()

    def execute_update(self, query, data):
        query = query % data
        logger.info('query：%s' % query)
        try:
            db_cursor = self.dbconn.cursor()
            db_cursor.execute(query)
            db_cursor.execute('commit')
            db_cursor.close()
            return ('', True)
        except Exception as e:
            logger.error('执行数据库更新操作失败：%s' % e)
            db_cursor.execute('rollback')
            db_cursor.close()
            return (e, False)

    def select_one_record(self, query, data=""):
        '''返回结果只包含一条记录'''
        logger.info('query：%s  data：%s' % (query, data))
        try:
            db_cursor = self.dbconn.cursor()
            if data:
                db_cursor.execute(query, data)
            else:
                db_cursor.execute(query)
            query_result = db_cursor.fetchone()
            self.dbconn.commit()
            db_cursor.close()
            return (query_result, True)
        except Exception as e:
            logger.error('执行数据库查询操作失败：%s' % e)
            db_cursor.close()
            return (e, False)

    def select_many_record(self, query, data=""):
        '''返回结果只包含多条记录'''
        logger.info('query：%s  data：%s' % (query, data))
        try:
            db_cursor = self.dbconn.cursor()
            if data:
                db_cursor.execute(query, data)
            else:
                db_cursor.execute(query)
            query_result = db_cursor.fetchall()
            self.dbconn.commit()
            db_cursor.close()
            return query_result
        except Exception as e:
            logger.error('执行数据库查询操作失败：%s' % e)
            db_cursor.close()
            exit()

    def close(self):
        self.dbconn.close
