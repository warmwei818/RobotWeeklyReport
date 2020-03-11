#!/usr/bin/env python
# encoding: utf-8

import configparser
import datetime
import json
import re
from enum import Enum

import requests


class Method(Enum):
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4


class Doc(object):
    title = ''
    id = ''

    def __repr__(self):
        return f'title: {self.title} | id: {self.id}'


class PageObject(object):
    doc_name = ''
    okr_progress_part = ''
    this_week_part = ''
    next_week_part = ''
    online_problem_part = ''
    data_modify_part = ''
    project_daily_part = ''


class RobotWeeklyReport(object):

    def __init__(self, cfg_filename):
        conf = configparser.ConfigParser()
        conf.read(cfg_filename)
        self._host = conf.get('base', 'api_host')
        self._report_doc_id = conf.get('base', 'report_doc_id')
        self._repo_id = conf.get('base', 'repo_id')
        self._user_agent = conf.get('base', 'user_agent')
        self._token = conf.get('base', 'yuque_token')
        self._namespace = conf.get('base', 'repo_namespace')
        self._robot_access_token = conf.get('base', 'dingding_access_token')
        self._doc_list = []
        self._merge_toast = ''
        self._save_toast = ''

    def send_request(self, method_type, path, params):
        url = self._host + path
        headers = {'User-Agent': self._user_agent, 'X-Auth-Token': self._token}

        if method_type is Method.GET:
            r = requests.get(url, headers=headers, params=params)
        elif method_type is Method.POST:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            r = requests.post(url, headers=headers, data=params)
        elif method_type is Method.PUT:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            r = requests.put(url, headers=headers, data=params)
        return r.json()

    # 获取知识库信息
    def fetch_repo(self):
        return self.send_request(Method.GET, f'repos/{self._repo_id}', {})

    # 获取各个业务组文档的id和title
    @staticmethod
    def fetch_group(repo_info):
        toc = repo_info['data']['toc']
        toc_list = toc.split('\n')
        output = []
        is_need_repo = False
        for item in toc_list:
            if is_need_repo:
                if item.startswith('  -', 0):
                    doc = Doc()
                    doc_title_search = re.search(r'\[(.*)\]', item)
                    doc_id_search = re.search(r'"(.*)"', item)
                    if doc_title_search:
                        doc.title = doc_title_search.group(1)
                    if doc_id_search:
                        doc.id = doc_id_search.group(1)
                    output.append(doc)
                else:
                    break
            if item.count('[XX部门开发各组周报]') > 0:
                is_need_repo = True
                continue
        return output

    # 获取doc的Markdown元数据
    def fetch_doc_markdown_data(self, doc_id):
        # raw = 1 返回的body为Markdown格式文本
        result = self.send_request(Method.GET, f'repos/{self._repo_id}/docs/{doc_id}', params={'raw': 1})
        return result['data']['body'], result['data']['title']

    # 创建语雀doc
    def create_report(self, body, title):
        url = f'repos/{self._namespace}/docs'
        params = {'title': title, 'body': body, 'public': 1}
        result = self.send_request(Method.POST, url, params)
        if 'data' in result:
            print('>>>>>>>> 历史周报创建成功 <<<<<<<<')
            self._save_toast = '历史周报创建成功；\n需要到语雀手动编辑目录添加到历史周报中'
        else:
            print('>>>>>>>> 历史周报创建失败 <<<<<<<<')
            self._save_toast = '历史周报创建失败'

    # 更新语雀doc,成功创建新doc存档到周报历史
    def update_report(self, body):
        date = str(datetime.date.today())
        url = f'repos/{self._repo_id}/docs/{self._report_doc_id}'
        params = {'title': '[自动生成-请勿编辑]XX部门开发周报' + date, 'public': 1, 'body': body}
        result = self.send_request(Method.PUT, url, params)

        if 'data' in result:
            print('>>>>>>>> 周报更新成功 <<<<<<<<')
            self._merge_toast = '周报汇总成功；\n'
            title = 'XX部门开发周报' + date
            self.create_report(body, title)
        else:
            print('>>>>>>>> 周报更新失败 <<<<<<<<')
            self._merge_toast = '周报汇总失败；\n'

    # 发送钉钉群消息
    def send_msg(self):
        url = f'https://oapi.dingtalk.com/robot/send?access_token={self._robot_access_token}'
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        if '成功' in self._merge_toast:
            merge_docs = f'合并的doc有：{self._doc_list}；\n'
        else:
            merge_docs = ''
        message = f'执行结果：{self._merge_toast}{merge_docs}{self._save_toast}'
        data = {
            "msgtype": "text",
            "text": {"content": message},
            "at": {
                "atMobiles": [
                    "1358812XXXX"
                ],
                # 1代表@所有人
                "isAtAll": 0
            }
        }
        msg_json = json.dumps(data)
        requests.post(url, data=msg_json, headers=headers)

    # 核心方法----合并多个doc组装成一个markdown文件，更新到指定doc
    def run(self):
        output = ''
        report = []
        repo_info = self.fetch_repo()
        work_docs = self.fetch_group(repo_info)

        work_doc_ids = list(map(lambda x: x.id, work_docs))
        for item in work_doc_ids:
            page = PageObject()
            result, title = self.fetch_doc_markdown_data(item)
            # 过滤字符串 形如：[](https://souche.yuque.com/bggh1p/weekly/bmkm6g#4181f001)
            result = re.sub('\\[\\]\\((.*)\\)', '', result)
            # 过滤字符串 形如：<a name="0a0310cf"></a>
            result = re.sub('<a(.*)</a>', '', result)
            self._doc_list.append(title)
            print('>>>>>>>>>>> ' + title + 'doc <<<<<<<<<<<<')
            page.doc_name = title
            page.okr_progress_part = re.findall('# OKR进度(.*)# 本周工作', result, re.DOTALL)[0].replace('#', '')
            page.this_week_part = re.findall('# 本周工作(.*)# 下周计划', result, re.DOTALL)[0].replace('#', '')
            page.next_week_part = re.findall('# 下周计划(.*)# 线上问题', result, re.DOTALL)[0].replace('#', '')
            page.online_problem_part = re.findall('# 线上问题(.*)# 数据订正', result, re.DOTALL)[0].replace('#', '')
            page.data_modify_part = re.findall('# 数据订正(.*)# 项目日常', result, re.DOTALL)[0].replace('#', '')
            page.project_daily_part = re.findall('# 项目日常(.*)', result, re.DOTALL)[0].replace('#', '')

            report.append(page)

        output += '## OKR进度\n'
        for item in report:
            output += f'\n### {item.doc_name}\n'
            output += item.okr_progress_part
        output += '\n## 本周工作\n'
        for item in report:
            output += f'\n### {item.doc_name}\n'
            output += item.this_week_part
        output += '\n## 下周计划\n'
        for item in report:
            output += f'\n### {item.doc_name}\n'
            output += item.next_week_part
        output += '\n## 线上问题\n'
        for item in report:
            output += f'\n### {item.doc_name}\n'
            output += item.online_problem_part
        output += '\n## 数据订正\n'
        for item in report:
            if '无\n' in item.data_modify_part:
                item.data_modify_part = ''
            output += item.data_modify_part
        output += '\n## 项目日常\n'
        for index, item in enumerate(report):
            daily_data_list = item.project_daily_part.split('\n')
            remove_empty_element_list = list(filter(None, daily_data_list))
            if index != 0:
                del remove_empty_element_list[:2]
            item.project_daily_part = '\n'.join(remove_empty_element_list)
            output += '\n' + item.project_daily_part
        with open('report_doc.md', 'w') as f:
            f.write(output)

        # step1: 语雀的坑一: 文档在语雀上编辑后，无法通过api更新。要么对文档做权限控制。
        # 当被人手动编辑后，需要重新api走一遍创建文档，以后方可使用api更新文档。
        # 语雀的坑二：创建后再语雀上并不显示，需要手动编辑目录管理添加doc到指定位置
        # self.create_report(output, 'XX部门开发周报')

        # step2: 已经创建文档后调用更新接口，并创建新文档保存到历史周报
        self.update_report(output)
        # step3: 执行结果发送到钉钉群组
        # self.send_msg()


if __name__ == "__main__":
    robot = RobotWeeklyReport('config_test.ini')
    robot.run()
