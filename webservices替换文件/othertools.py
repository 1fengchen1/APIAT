#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'shouke'

import os
import re

class OtherTools:
    def __init__(self):
        self.dict_level_list = []
        self.key_index = 0
        pass

    def conver_date_from_testlink(self, data):
        '''加工处理从testlink获取的数据'''

        data =  data.replace('\t', '')
        data =  data.replace('\n', '')
        data =  data.replace('&nbsp;', ' ')    # 替换空格
        data =  data.replace('&rsquo;', '"')   # 转换中文单引号 ’为英文的 "
        data =  data.replace('&lsquo;', '"')   # 转换中文单引号‘ 为英文的 "
        data =  data.replace('&ldquo;', '"')   # 转换中文双引号“ 为英文的 "
        data =  data.replace('&rdquo;', '"')   # 转换中文双引号 ” 为英文的 "
        data =  data.replace('：', ":")         # 转换中文的冒号 ：为英文的冒号 :
        data =  data.replace('，', ',')         # 转换中文的逗号 ，为英文的逗号 ,
        data =  data.replace('&quot;', '\"')   # 转换 &quot; 为双引号
        data =  data.replace('&#39;', '\'')    # 转换 &#39;  为单引号
        data =  data.replace('｛', '{')         # 转换中文｛ 为英文的 {
        data =  data.replace('｝', '}')         # 转换中文 ｝ 为英文的 }
        data =  data.replace('&lt;', '<')      # 转换 &lt; 为 <
        data =  data.replace('&gt;', '>')      # 转换 &gt为 >
        data = data.replace('&amp;','&')
        data = data.replace('【','[')
        data = data.replace('】',']')
		
        result_list = ['</p>','</ol>', '</div>','</span>', '<p>', '</strong>','</em>','</u>','</pre>','</li>','</strike>']
        for item in result_list:
            if item in data:
                data = data.replace(item, '')
        
        result_list = []
        patterns = ['<br', '<div', '<span', '<li','<pre', '</ol','<strong','<em', '<p ', '<u ', '<strike']
        for pattern in patterns:
           pattern = pattern + '.?[^<]*>'
           result_list = result_list + re.findall(pattern, data)

        if result_list:
            for item in result_list:
                data = data.replace(item,'')

        # 防止用户在step_action中输入大写的或者大小写混合的url key名称，转换为小写
        url_str_list = [',"Url":',',"uRl":',',"urL":',',"URl"',',"uRL":','"UrL":','"URL":']
        for item in url_str_list:
            if data.find(item) != -1:
                data = data.replace(item, ',url:')
        return  data

    # 批量创建目录
    def mkdirs_once_many(self, path):
        path = os.path.normpath(path)  # 去掉路径最右侧的 \\ 、/
        path = path.replace('\\', '/') # 将所有的\\转为/，避免出现转义字符串

        head, tail = os.path.split(path)
        new_dir_path = ''  # 反转后的目录路径
        root = ''  #根目录

        if not os.path.isdir(path) and os.path.isfile(path):  # 如果path指向的是文件，则继续分解文件所在目录
            head, tail = os.path.split(head)

        if tail == '':
            return

        while tail:
            new_dir_path = new_dir_path + tail + '/'
            head, tail = os.path.split(head)
            root = head
        else:
            new_dir_path = root + new_dir_path
            # print(new_dir_path)

            # 批量创建目录
            new_dir_path = os.path.normpath(new_dir_path)
            head, tail = os.path.split(new_dir_path)
            temp = ''
            while tail:
                temp = temp + '/' + tail
                dir_path = root + temp
                if not os.path.isdir(dir_path):
                    os.mkdir(dir_path)
                head, tail = os.path.split(head)

    # 获取给定字典的所有key,value层级
    def get_dict_level_list(self,pattern_dic):
        all_keys = pattern_dic.keys()

        for key in all_keys:
            value = pattern_dic.get(key)
            self.dict_level_list.append(key)  #用于存放层级及key值
            if type(value) == type({}):
                self.get_dict_level_list(value)
            else:
                self.dict_level_list.append(value)
        return self.dict_level_list[:]

    def find_dict_last_leve_value(self, dict_level_list, dict):
        global  key_index
        # 在字典中查找对应层级，对应key的value值
        for key_level in dict_level_list[self.key_index:len(dict_level_list) -1]:
            result = dict.get(key_level)
            if result == None: # 如果还没遍历完成所有key就发现找不到对应层级的key，提前结束,节约时间
                return result
            elif type(result) == type([]): # 获取的值为列表，形如[{"goodsId":1,"goods_name":"apple"},{"goodsId":2,"goods_name":"apple"}]
                # 遍历列表,每个字典中查找
                self.key_index = self.key_index + 1
                for dic_item in result:
                    result = self.find_dict_last_leve_value(dict_level_list, dic_item)
                    if result != None: # 找到了
                        return result
            elif type(result) == type({}): # 获取的值为字典，形如{"goodsId":1,"goods_name":"apple"}
                # 在该字典中查找
                self.key_index = self.key_index + 1
                result = self.find_dict_last_leve_value(dict_level_list, result)
                if result != None:
                    return result # 找到了
            else:
                return  result

    def set_key_index(self,key_index):
        self.key_index = key_index

    def set_dict_level_list(self,dict_level_list):
        self.dict_level_list = dict_level_list









