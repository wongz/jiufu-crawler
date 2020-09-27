#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import random
import codecs
import csv
import json
import traceback
from collections import OrderedDict
from datetime import datetime
from threading import Thread
from time import sleep

import requests
from lxml import etree
from requests.adapters import HTTPAdapter
from hyper.contrib import HTTP20Adapter


class Jiufu(object):
    def __init__(self, token):
        self.creditors = []
        self.got_count = 0
        self.orders = []
        self.order_no = 'ALL_ORDERS'
        self.date_str = datetime.now().strftime('%Y%m%d%H%M%S')
        self.token = token.replace('token:', '').replace('"', '').strip()
        self.dl_tag = 'n'
        self.thread = Thread(target=self.dl_choose, daemon=False)
        self.thread.start()
        sleep(5)
        if self.dl_tag.strip() in ['y', 'Y', '1']:
            self.dl = 1
            self.limit = 10
        else:
            self.dl = 0
            self.limit = 100

    def dl_choose(self):
        print('')
        self.dl_tag = input(u'请在5秒内选择是否下载附件(默认不下载，若下载耗时较长)(Y/n)? ')

    def get_headers(self, url):
        headers = {
            ':authority': 'm.wukonglicai.com',
            ':method': 'POST',
            ':path': url.replace('https://m.wukonglicai.com', ''),
            ':scheme': 'https',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'content-length': '198',
            'content-type': 'application/json; charset=UTF-8',
            'referer': 'https://m.wukonglicai.com/weChat/order/order-list?type=Y',
            'deviceid': '',
            'dnt': '1',
            'origin': 'https://m.wukonglicai.com',
            'phonetype': '',
            'platform': 'WEIXIN',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sysversion': '',
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Mobile Safari/537.36',
            'useragent': '',
            'version': ''
            #'cookie': self.cookie
        }
        return headers

    def get_creditor_json(self, page):
        url = 'https://m.wukonglicai.com/wklc-api/creditor/creditor-rights/list'
        params = {
            'orderNo': self.order_no,
            'pageNo': page,
            'pageSize': self.limit,
            'token': self.token
        }
        sessions = requests.session()
        sessions.mount('https://m.wukonglicai.com', HTTP20Adapter())
        resp = sessions.post(url, data=json.dumps(params), headers=self.get_headers(url))
        return resp.json()

    def get_order_json(self, page):
        url = 'https://m.wukonglicai.com/wklc-api/order/query/order-list'
        params = {
            'token': self.token,
            'productCat': 'Y',
            'assetType': '',
            'orderStatus': '0',
            'sortField': 'P',
            'continueStatus': '',
            'pageSize': 10,
            'operChannel': 'WKLC',
            'sortType': 1,
            'pageNo': page
        }
        sessions = requests.session()
        sessions.mount('https://m.wukonglicai.com', HTTP20Adapter())
        resp = sessions.post(url, data=json.dumps(params), headers=self.get_headers(url))
        return resp.json()

    def check_need_login(self, resp):
        page = etree.HTML(resp.text)
        titles = page.xpath('/html/head/title')
        for title in titles:
            if u'登录' in title.text:
                raise RuntimeError(u'Cookie失效，请在浏览器上登录获取Cookie后重试。')

    def get_orders(self):
        page = 0
        wrote_count = 0
        print('')
        print(u'{}订单列表开始获取{}'.format('-' * 20, '-' * 25))
        while 1:
            page += 1
            js = self.get_order_json(page)
            if js['code'] == '000000':
                orders = js['data']['orders']
                if len(orders) == 0:  # 订单爬取结束
                    count = 0
                    for order in self.orders:
                        count += 1
                        print(u'{} {} {}'.format(order['orderNo'], order['orderAmount'], order['orderStatusDesc']))
                    print(u'{}共获取到{}笔订单{}'.format('-' * 20, count, '-' * 25))
                    print('')
                    self.write_data(self.orders, wrote_count)
                    return
                for order in orders:
                    #order['orderAmount'] = order['orderAmount'].replace(',', '')    #   Windows平台写入csv错误
                    self.orders.append(order)
                    self.got_count += 1
            else:
                raise RuntimeError(js['message'])

    def get_creditors(self):
        page = 0
        page_count = 1000
        wrote_count = 0
        page1 = 0
        random_pages = random.randint(1, 5)
        print(u'{}订单号{}开始爬取{}'.format('-' * 10, self.order_no, '-' * 10))
        while 1:
            page += 1
            js = self.get_creditor_json(page)
            if js['code'] == '000000':
                creditors = js['data']['list']
                for creditor in creditors:
                    self.creditors.append(creditor)
                    self.got_count += 1
                    if self.dl:
                        self.download_file(creditor['argeeUrl'], 'pdf')
                        self.download_file(creditor['letterGuarantee'], 'pdf')
                print(u'{} - 已获取第{}页的{}条记录'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), page, len(creditors)))
            elif js['code'] == '000002':
                self.write_data(self.creditors, wrote_count)
                print(u'{}此订单完成爬取，共爬取{}条记录{}'.format('-' * 10, self.got_count, '-' * 20))
                print('')
                break
            else:
                raise RuntimeError(js['message'])
            if page % 20 == 0:  # 每爬20页写入一次文件
                self.write_data(self.creditors, wrote_count)
                wrote_count = self.got_count
            if (page - page1) % random_pages == 0 and page < page_count:
                sleep(random.randint(1, 3))
                page1 = page
                random_pages = random.randint(1, 5)

    def get_result_headers(self, result_data):
        """"获取要写入结果文件的表头"""
        result_headers = []
        for k, v in result_data[0].items():
            result_headers.append(k)
        return result_headers

    def get_filepath(self, file_type):
        """获取结果文件路径"""
        try:
            file_dir = os.path.split(
                os.path.realpath(__file__)
            )[0] + os.sep + self.date_str
            if file_type in ['img', 'video', 'pdf']:
                file_dir = file_dir + os.sep + self.order_no
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)
            if file_type in ['img', 'video', 'pdf']:
                return file_dir
            file_path = file_dir + os.sep + self.order_no + '.' + file_type
            return file_path
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def write_csv(self, result_data):
        """将爬到的信息写入csv文件"""
        result_headers = self.get_result_headers(result_data)
        result_data = [list(w.values()) for w in result_data]
        file_path = self.get_filepath('csv')
        self.csv_helper(result_headers, result_data, file_path)


    def csv_helper(self, headers, result_data, file_path):
        """将指定信息写入csv文件"""
        if not os.path.isfile(file_path):
            is_first_write = 1
        else:
            is_first_write = 0
        with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            if is_first_write:
                writer.writerows([headers])
            writer.writerows(result_data)
        #	print(u'{} - {}条记录已写入文件：{}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.got_count, file_path))

    def write_data(self, result_data, wrote_count):
        """将爬到的信息写入文件或数据库"""
        if self.got_count > wrote_count:
            self.write_csv(result_data)

    def download_file(self, url, file_type):
        if not url.strip():
            return
        file_path = self.get_filepath(file_type) + os.sep + url.split('=')[1] + '.' + file_type
        try:
            if not os.path.isfile(file_path):
                s = requests.Session()
                s.mount(url, HTTPAdapter(max_retries=5))
                downloaded = s.get(url, cookies={'Cookie': self.cookie}, timeout=(5, 10))
                with open(file_path, 'wb') as f:  # w写,b二进制
                    f.write(downloaded.content)
        except Exception as e:
            error_file = self.get_filepath(
                file_type) + os.sep + 'not_downloaded.txt'
            with open(error_file, 'ab') as f:
                url = str(self.order_no) + ':' + file_path + ':' + url + '\n'
                f.write(url.encode(sys.stdout.encoding))
            print('Error: ', e)
            traceback.print_exc()

    def initialize_info(self, order_no):
        """初始化爬虫信息"""
        self.creditors = []  # 重置
        self.got_count = 0  # 重置
        self.order_no = order_no  # 遍历订单号

    def start(self):
        """运行爬虫"""
        try:
            self.get_orders()
            for order in self.orders:
                self.initialize_info(order['orderNo'])
                self.get_creditors()
            print(u'信息抓取完毕，文件保存在 %s 目录下。' %
                  (os.path.split(os.path.realpath(__file__))[0] + os.sep + self.date_str))
        except Exception as e:
            print('Error: ', e)
            # traceback.print_exc()
        finally:
            # os.system('pause') # 打包为exe，执行完后等待关闭窗口
            # print(u'程序将在30秒后自动退出...')
            # sleep(30)
            print('')
            if self.thread.is_alive():
                print(u'请按回车键退出...')  # 线程等待输入会影响进程退出
            else:
                input(u'请按回车键退出...')


def main():
    print(u'{}悟空理财导出工具 v{}{}'.format('-' * 20, 1.0, '-' * 20))
    print('')
    print(u'说明：谷歌浏览器按F12打开控制台，在m.wukonglicai.com登录成功后，依次点击'
          u'Network->Name列表中的affirm->Preview->展开data，复制出token，像下面这种：')
    print(u'[BB120300-4a7ae99fa2b245068588cd963d948a33]')
    print('')
    if not os.path.isfile('./token.txt'):
        token = input(u'工作目录下无token.txt文件，请输入token：')
    else:
        with open('./token.txt') as f:
            token = f.read()
            print(u'读取到工作目录下的token.txt文件。')
    jf = Jiufu(token)
    jf.start()


if __name__ == '__main__':
    main()
