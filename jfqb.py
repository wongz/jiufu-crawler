#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import random
import codecs
import csv
import traceback
from datetime import datetime
from threading import Thread
from time import sleep

import requests
from lxml import etree
from requests.adapters import HTTPAdapter


class Jiufu(object):
    def __init__(self, cookie):
        self.creditors = []
        self.got_count = 0
        self.orders = []
        self.order_no = 'ALL_ORDERS'
        self.date_str = datetime.now().strftime('%Y%m%d%H%M%S')
        self.cookie = cookie.replace('Cookie:', '').strip()
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
        self.dl_tag = input(u'请在 5 秒内选择是否下载附件(默认不下载，若下载耗时较长)? [Y/n] ')

    def get_creditor_html(self, page):
        url = 'https://8.9fpuhui.com/userCenter2/queryWlzZpListdata.html?'
        params = {
            'orderNo': self.order_no,
            'pageNum': page,
            'pageSize': self.limit
        }
        cookie = {'Cookie': self.cookie}
        resp = requests.post(url, params=params, cookies=cookie)
        self.check_need_login(resp)
        return resp.text

    def get_order_html(self, page):
        url = 'https://8.9fpuhui.com/userCenter2/investCount2ListData.html?'
        params = {
            'status': 0,
            'productCatCode': '',
            'productName': '',
            'selectName': '',
            'page': page
        }
        cookie = {'Cookie': self.cookie}
        resp = requests.post(url, params=params, cookies=cookie)
        self.check_need_login(resp)
        return resp.text

    def check_need_login(self, resp):
        page = etree.HTML(resp.text)
        titles = page.xpath('/html/head/title')
        for title in titles:
            if u'登录' in title.text:
                raise RuntimeError(u'Cookie失效，请在浏览器上登录获取Cookie后重试。')

    def get_orders(self):
        page = 0
        print('')
        print(u'{}订单列表开始获取{}'.format('-' * 20, '-' * 25))
        while 1:
            page += 1
            html = self.get_order_html(page)
            selector = etree.HTML(html)
            rows = selector.xpath('//*[@id="dataDiv"]/div')  # /div[3]/p[2]/a
            for row in rows:
                order = []
                selector = row.xpath('./div[3]/p[2]/a')
                if len(selector) == 0:  #   现金券，非订单
                    continue
                order_no = selector[0].get('href')[61:]
                order.append(order_no)  # 订单号
                selector = row.xpath('./div[1]/p')
                order.append(selector[0].text.strip())  # 1产品名称
                order.append(selector[1].xpath('./span')[1].text)  # 2加入时间
                order.append(selector[2].xpath('./span')[1].text)  # 3加入金额
                order.append(selector[3].xpath('./span')[1].text)  # 4起算回报日期
                selector = row.xpath('./div[3]/dl/dd')
                order.append(selector[0].xpath('./span')[1].text)  # 5参考年回报率
                order.append(selector[1].xpath('./span')[1].text)  # 6服务期
                order.append(selector[2].xpath('./span')[1].text)  # 7期望服务期满总回报
                order.append(selector[3].xpath('./span') and selector[3].xpath('./span')[0].text)  # 8服务期届满处理方式
                order.append(selector[4].xpath('./span')[0].text)  # 9服务期届满时间
                order.append(selector[4].xpath('./span')[1].text)  # 剩余天数
                if order_no in [order[0] for order in self.orders]:
                    count = 0
                    for order in self.orders:
                        count += 1
                        print(u'{} {} {} {}'.format(order[0], order[4], order[9],
                                                    order[3].replace('¥', 'Y')))  # unicode输出到cmd为gbk，不支持'¥'编码
                        if self.dl:
                            self.download_file('https://8.9fpuhui.com/userCenter2/downloadOrderContract.html?orderNo='
                                               + order[0] + '&1', 'pdf')  # 出借咨询及管理服务协议
                            self.download_file('https://8.9fpuhui.com/antiMoneyLaundering/download.html?orderNo='
                                               + order[0] + '&2=&orderType=YX', 'pdf')  # 授权委托、反洗钱及出借风险提示书
                            self.download_file('https://8.9fpuhui.com/digitalContract/download.html?orderNo='
                                               + order[0] + '&3=&orderType=YX', 'pdf')  # 数字证书申请表及授权委托书
                    print(u'{}共获取到{}笔订单{}'.format('-' * 20, count, '-' * 25))
                    print('')
                    result_headers = ['订单号', '产品名称', '加入时间', '加入金额', '起算回报日期', '参考年回报率',
                                      '服务期', '期望服务期满总回报', '服务期届满处理方式', '服务期届满时间', '剩余天数']
                    result_data = self.orders
                    file_path = self.get_filepath('csv')
                    self.csv_helper(result_headers, result_data, file_path)
                    return
                else:
                    self.orders.append(order)

    def get_one_page(self, page):
        try:
            html = self.get_creditor_html(page)
            selector = etree.HTML(html)
            # print(etree.tostring(selector).decode('utf-8'))
            rows = selector.xpath('/html/body/div[3]/table/tr')
            if len(rows) == 0:
                return True
            creditor = []
            for row in rows:
                if row.get('class') == 'zq-tdt':  # 标题行
                    continue
                else:
                    cols = row.xpath('./td')
                    if row.get('class') == 'checks_ct':
                        cols = row.xpath('./td/div/div/span[2]')
                    for col in cols:
                        text = col.text
                        if text:
                            text = text.strip()
                            if text == '':
                                other = col.xpath('./input')
                                if len(other) > 0:
                                    text = other[0].get('value')
                        else:
                            other = col.xpath('./a')
                            if len(other) > 0:
                                text = other[0].get('href')
                                if self.dl and text:
                                    self.download_file(text, 'pdf')
                        creditor.append(text)
                    if row.get('class') == 'checks_ct':  # 更多信息
                        self.creditors.append(creditor)
                        self.got_count += 1
                        creditor = []  # 两行处理结束清空集合
            print(u'{} - 已获取第{}页的{}条记录'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), page,
                                               int((len(rows) - 1) / 2)))
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_result_headers(self):
        """获取要写入结果文件的表头"""
        result_headers = ['序号', '借款方', '证件号/凭证号', '借款用途', '借出金额', '借款合同期限', '保单号', '借款协议', '担保函', 'appid', '经营状况及财务状况',
                          '还款能力变化情况', '逾期情况', '涉讼情况', '受行政处罚情况', '其他影响还款的重大信息', '还款保障措施', '交易时剩余未还期数',
                          '交易时借款合同是否到期', '借款到期后贷后是否在追踪延期还款']
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

    def write_csv(self):
        result_headers = self.get_result_headers()
        result_data = self.creditors
        file_path = self.get_filepath('csv')
        self.csv_helper(result_headers, result_data, file_path)

    def csv_helper(self, headers, result_data, file_path):
        """将指定信息写入csv文件"""
        if not os.path.isfile(file_path):
            is_first_write = 1
        else:
            is_first_write = 0
        if sys.version < '3':  # python2.x
            with open(file_path, 'ab') as f:
                f.write(codecs.BOM_UTF8)
                writer = csv.writer(f)
                if is_first_write:
                    writer.writerows([headers])
                writer.writerows(result_data)
        else:  # python3.x
            with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if is_first_write:
                    writer.writerows([headers])
                writer.writerows(result_data)
        #	print(u'{} - {}条记录已写入文件：{}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.got_count, file_path))

    def write_data(self, wrote_count):
        """将爬到的信息写入文件或数据库"""
        if self.got_count > wrote_count:
            self.write_csv()

    def download_file(self, url, file_type):
        file_path = self.get_filepath(file_type) + os.sep + url.split('=')[1] + '.' + file_type
        try:
            if not os.path.isfile(file_path):
                s = requests.Session()
                s.mount(url, HTTPAdapter(max_retries=5))
                downloaded = s.get(url, cookies={'Cookie': self.cookie}, stream=True, timeout=(5, 10))
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

    def get_pages(self):
        try:
            # page_count = 1000
            wrote_count = 0
            page1 = 0
            random_pages = random.randint(1, 5)
            page = 0
            print(u'{}订单号{}开始爬取{}'.format('-' * 10, self.order_no, '-' * 10))
            while 1:
                page += 1
                is_end = self.get_one_page(page)
                if is_end:
                    break
                # if page % 20 == 0:  # 每爬20页写入一次文件
                #   self.write_data(wrote_count)
                #    wrote_count = self.got_count

                # 通过加入随机等待避免被限制。爬虫速度过快容易被系统限制(一段时间后限
                # 制会自动解除)，加入随机等待模拟人的操作，可降低被系统限制的风险。
                # 默认是每爬取1到5页随机等待1到3秒，如果仍然被限，可适当增加sleep时间
                if (page - page1) % random_pages == 0:  # and page < page_count:
                    sleep(random.randint(1, 3))
                    page1 = page
                    random_pages = random.randint(1, 5)
            self.write_data(wrote_count)
            print(u'{}此订单完成爬取，共爬取{}条记录{}'.format('-' * 10, self.got_count, '-' * 20))
            print('')

        except Exception as e:
            print("Error: ", e)
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
                self.initialize_info(order[0])
                self.get_pages()
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
    print(u'{}玖富钱包导出工具 v{}{}'.format('-' * 20, 1.3, '-' * 20))
    print('')
    print(u'说明：谷歌浏览器先按F12打开控制台，输入 https://8.9fpuhui.com/login.html 登录成功后，依次点击'
          u'Network -> Name列表中的checkLogin.html -> Headers -> Request Headers，复制出Cookie，像下面这种：')
    print(u'[Cookie: cookId=78b***; JSESSIONID=9B2***; logintoken=a01***]')
    print('')
    if not os.path.isfile('./cookie.txt'):
        cookie = input(u'工作目录下无cookie.txt文件，请输入Cookie：')
    else:
        with open('./cookie.txt') as f:
            cookie = f.read()
            print(u'读取到工作目录下的cookie.txt文件。')
    jf = Jiufu(cookie)
    jf.start()


if __name__ == '__main__':
    main()
