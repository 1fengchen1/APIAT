#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'shouke'

import urllib.request
import http.cookiejar
import urllib.parse
import ssl
import configparser
from globalpkg.log import logger

# 添加cookie自动处理支持
cj = http.cookiejar.CookieJar()
cookie_handler = urllib.request.HTTPCookieProcessor(cj)

# 添加ssl支持 # 注意，发起的请求要为443端口
config = configparser.ConfigParser()

try:
    config.read('./config/https.conf', encoding='utf-8-sig')
    ssl_or_tls_protocol = config['HTTPS']['SSL_OR_TLS_PROTOCOL'].lower()
except Exception as e:
    print('读取HTTPS SSL|TSL配置错误:%s' % e)
    exit(1)

if ssl_or_tls_protocol == 'v1':
    https_handler = urllib.request.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
elif ssl_or_tls_protocol == 'v2':
    https_handler = urllib.request.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv2))
elif ssl_or_tls_protocol == 'v23':
    https_handler = urllib.request.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv23))
elif ssl_or_tls_protocol == 'v3':
    https_handler = urllib.request.HTTPSHandler(context=ssl.PROTOCOL_SSLv3)
opener = urllib.request.build_opener(cookie_handler, https_handler)
urllib.request.install_opener(opener)


class MyHttp:
    '''配置要测试接口服务器的ip、端口、域名等信息，封装http请求方法，http头设置'''

    def __init__(self, protocol, host, port, header={}):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.headers = header  # http 头

    def set_host(self, host):
        self.host = host

    def get_host(self):
        return self.host

    def get_protocol(self):
        return self.protocol

    def set_port(self, port):
        self.port = port

    def get_port(self):
        return self.port

    # 设置http头
    def set_header(self, headers):
        self.headers = headers

    # 封装HTTP GET请求方法
    def get(self, url, params=''):

        # url = self.protocol + '://' + self.host + ':' + str(self.port) + url + params

        if str(self.port) == '':
            # 端口号不填，就是默认的80
            url = self.protocol + '://' + self.host + url + params
        else:
            # 端口号有值，加上端口号
            url = self.protocol + '://' + self.host + ':' + str(self.port) + url + params

        logger.info('发起的请求为：%s' % url)
        logger.info('请求头为：%s' % self.headers)
        request = urllib.request.Request(url, headers=self.headers)
        exec_count = 0
        while exec_count <= 1:
            try:
                response = urllib.request.urlopen(request)
                response_body = response.read()
                response_header = response.getheaders()
                response_status_code = response.status
                response = [response_body, response_header, response_status_code]
                exec_count = 2
            except Exception as e:
                exec_count = exec_count + 1
                reason = '%s' % e
                response = [None, reason]
                print('发送请求失败，原因：%s,正在进行第%s次尝试' % (e, exec_count))
        return response

    # 封装HTTP POST请求方法
    def post(self, url, data=b''):

        # url = self.protocol + '://' + self.host + ':' + str(self.port) + url

        if str(self.port) == '':
            # 端口号不填，就是默认的80
            url = self.protocol + '://' + self.host + url
        else:
            # 端口号有值，加上端口号
            url = self.protocol + '://' + self.host + ':' + str(self.port) + url


        logger.info('发起的请求为：%s' % url)
        logger.info('参数为：%s' % data)
        logger.info('请求头为：%s' % self.headers)
        request = urllib.request.Request(url, headers=self.headers, method='POST')
        exec_count = 0
        while exec_count <= 1:
            try:
                response = urllib.request.urlopen(request, data)
                response_body = response.read()
                response_header = response.getheaders()
                response_status_code = response.status
                response = [response_body, response_header, response_status_code]
                exec_count = 2
            except Exception as e:
                exec_count = exec_count + 1
                reason = '%s' % e
                response = [None, reason]
                print('发送请求失败，原因：%s,正在进行第%s次尝试' % (e, exec_count))
        return response

    # 封装HTTP xxx请求方法
    # 自由扩展
