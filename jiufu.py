#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import random
import codecs
import csv
import json
import traceback
from datetime import datetime
from threading import Thread
from time import sleep

import requests
from lxml import etree
from requests.adapters import HTTPAdapter
from hyper.contrib import HTTP20Adapter


class Jiufu(object):
    def __init__(self, config):
        self.creditors = []
        self.got_count = 0
        self.orders = []
        self.order_no = 'ALL_ORDERS'
        self.date_str = datetime.now().strftime('%Y%m%d%H%M%S')
        self.config = config
        self.thread = None

    def init_config(self):
        config = self.config
        print('')
        if 'logintoken' in config:
            print(u'{}玖富普惠{}'.format('-' * 25, '-' * 25))
            self.cookie = config.replace('Cookie:', '').strip()
            self.token = None
        elif '-' in config:
            print(u'{}悟空理财{}'.format('-' * 25, '-' * 25))
            self.cookie = None
            self.token = config.replace('token:', '').replace('"', '').strip()
        else:
            raise RuntimeError(u'输入的内容有误')
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
        self.header_cn = {
            'freePlan': '免费计划freePlan',
            'lineThrough': '直通lineThrough',
            'productCat': '产品productCat',
            'exceptProfit': '累计期望回报',
            'allowEdit': '可续期allowEdit',
            'orderStatus': '订单状态',
            'expireProcessDesc': '封闭期满处理方式',
            'cumulativeDesc': '累计期望回报',
            'orderContinueStatus': '续期',
            'orderNo': '订单编号',
            'inFullClaims': '全额索赔inFullClaims',
            'orderStatusDesc': '订单状态说明',
            'transferRate': '转让利率transferRate',
            'productName': '产品名称',
            'operChannel': '操作渠道',
            'orderAmount': '出借金额',
            'sanbiaoMainOrderNo': '散标订单号',
            'remainDays': '剩余天数',
            'source': '来源source',
            'totalYield': '期望年化回报率',
            'assetType': '资产类型assetType',
            'contractIsExpire': '交易时借款合同是否到期',
            'argeeUrl': '债权协议',
            'matchAmount': '借出金额',
            'repayAbility': '还款能力变化情况',
            'loanName': '借款方',
            'repaySafeguards': '还款保障措施',
            'extendsRatio': '延伸率extendsRatio',
            'agreeType': '同意类型agreeType',
            'policyNo': '保单编号policyNo',
            'remainingIssuePeriod': '交易时剩余未还期数',
            'repayIsTrack': '借款到期后贷后是否在追踪延期还款',
            'securityProgramDesc': '第三方限额保障计划Desc',
            'operatingConditions': '经营状况及财务状况',
            'overdueSituation': '逾期情况',
            'loanPeriod': '借款合同期限',
            'assignorType': '转让类型assignorType',
            'loanCardNo': '证件号',
            'caseLitigiousLitigation': '涉诉情况',
            'loanPurpose': '资金运用情况',
            'otherRepayInfo': '其他还款信息otherRepayInfo',
            'securityProgramUrl': '第三方限额保障计划Url',
            'letterGuarantee': '信用担保letterGuarantee',
            'administrativePenalties': '受行政处罚情况'
        }

    def dl_choose(self):
        print('')
        self.dl_tag = input(u'请在 5 秒内选择是否下载附件(默认不下载，若下载耗时较长)? [Y/n] ')

    def get_orders(self):
        page = 0
        print('')
        print(u'{}获取订单列表{}'.format('-' * 20, '-' * 20))
        while True:
            page += 1
            if self.cookie:
                is_end = self.get_one_page_orders(page)
            if self.token:
                is_end = self.get_one_page_orders_wklc(page)
            if is_end:
                result_headers = ['订单号', '产品名称', '加入时间', '加入金额', '起算回报日期', '参考年回报率',
                                  '服务期', '期望服务期满总回报', '服务期届满处理方式', '服务期届满时间', '剩余天数']
                result_data = self.orders
                if self.token:
                    result_headers = self.get_result_headers(result_data)
                    result_data = [list(w.values()) for w in result_data]
                file_path = self.get_filepath('csv')
                self.csv_helper(result_headers, result_data, file_path)
                print(u'{}获取 {} 笔订单{}'.format('-' * 20, len(self.orders), '-' * 20))
                print('')
                break

    def initialize_info(self, order_no):
        """初始化爬虫信息"""
        self.creditors = []  # 重置
        self.got_count = 0  # 重置
        self.order_no = order_no #赋值

    def get_creditors(self):
        wrote_count = 0
        page1 = 0
        random_pages = random.randint(1, 5)
        page = 0
        print(u'{}处理订单 {}{}'.format('-' * 10, self.order_no, '-' * 10))
        while True:
            page += 1
            if self.cookie:
                is_end = self.get_one_page_creditors(page)
            if self.token:
                is_end = self.get_one_page_creditors_wklc(page)
            if is_end:
                # 全部写入文件
                result_headers = ['序号', '借款方', '证件号/凭证号', '借款用途', '借出金额', '借款合同期限', '保单号', '借款协议', '担保函', 'appid', '经营状况及财务状况',
                          '还款能力变化情况', '逾期情况', '涉讼情况', '受行政处罚情况', '其他影响还款的重大信息', '还款保障措施', '交易时剩余未还期数',
                          '交易时借款合同是否到期', '借款到期后贷后是否在追踪延期还款']
                result_data = self.creditors
                if self.token:
                    result_headers = self.get_result_headers(result_data)
                    result_data = [list(w.values()) for w in result_data]
                file_path = self.get_filepath('csv')
                self.csv_helper(result_headers, result_data, file_path)
                print(u'{}此订单处理完毕，共获取了 {} 条记录{}'.format('-' * 10, self.got_count, '-' * 10))
                print('')
                break
            # if page % 20 == 0:  # 每爬20页写入一次文件
            #     self.write_data(wrote_count)
            #     wrote_count = self.got_count
            # 通过加入随机等待避免被限制。爬虫速度过快容易被系统限制(一段时间后限
            # 制会自动解除)，加入随机等待模拟人的操作，可降低被系统限制的风险。
            # 默认是每爬取1到5页随机等待1到3秒，如果仍然被限，可适当增加sleep时间
            if (page - page1) % random_pages == 0:
                sleep(random.randint(1, 3))
                page1 = page
                random_pages = random.randint(1, 5)

    def get_creditor_html(self, page):
        url = 'https://8.9fpuhui.com/userCenter2/queryWlzZpListdata.html'
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
        url = 'https://8.9fpuhui.com/userCenter2/investCount2ListData.html'
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
                raise RuntimeError(u'登录失败，请重新登录（Cookie失效）')

    def get_headers(self, url):
        headers = {
            ':authority': 'm.wukonglicai.com',
            ':method': 'POST',
            ':path': url.replace('https://m.wukonglicai.com', ''),
            ':scheme': 'https',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
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
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Mobile Safari/537.36',
            'useragent': '',
            'version': ''
            # 'cookie': self.cookie
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
            'productCat': '',
            'assetType': '',
            'orderStatus': '0',  # 0未结束的订单,1已结束
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

    def get_one_page_orders(self, page):
        html = self.get_order_html(page)
        selector = etree.HTML(html)
        rows = selector.xpath('//*[@id="dataDiv"]/div')  # /div[3]/p[2]/a
        for row in rows:
            order = []
            selector = row.xpath('./div[3]/p[2]/a')
            if len(selector) == 0: # 优惠券非出借订单
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
                return True
            else:
                self.orders.append(order)

    def get_one_page_orders_wklc(self, page):
        js = self.get_order_json(page)
        if js['code'] == '000000':
            orders = js['data']['orders']
            if len(orders) == 0:  # 订单爬取结束
                count = 0
                for order in self.orders:
                    count += 1
                    print(u'{} {} {}'.format(order['orderNo'], order['orderAmount'], order['orderStatusDesc']))
                return True
            for order in orders:
                self.orders.append(order)
                self.got_count += 1
        else:
            raise RuntimeError(js['message'])

    def get_one_page_creditors(self, page):
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
        print(u'{} - 已获取第 {} 页的 {} 条记录'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), page,
                                               int((len(rows) - 1) / 2)))

    def get_one_page_creditors_wklc(self, page):
        js = self.get_creditor_json(page)
        if js['code'] == '000000':
            creditors = js['data']['list']
            for creditor in creditors:
                self.creditors.append(creditor)
                self.got_count += 1
                if self.dl:
                    self.download_file(creditor['argeeUrl'], 'pdf')
                    self.download_file(creditor['letterGuarantee'], 'pdf')
            print(u'{} - 已获取第 {} 页的 {} 条记录'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), page, len(creditors)))
        elif js['code'] == '000002':
            return True
        else:
            raise RuntimeError(js['message'])

    def get_result_headers(self, result_data):
        """获取要写入结果文件的表头"""
        result_headers = []
        for k, v in result_data[0].items():
            result_headers.append(self.header_cn[k])
        return result_headers

    def get_filepath(self, file_type):
        """获取结果文件路径"""
        file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + self.date_str
        if file_type in ['img', 'video', 'pdf']:
            file_dir = file_dir + os.sep + self.order_no
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        if file_type in ['img', 'video', 'pdf']:
            return file_dir
        file_path = file_dir + os.sep + self.order_no + '.' + file_type
        return file_path

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

    def download_file(self, url, file_type):
        file_path = self.get_filepath(file_type) + os.sep + url.split('=')[1] + '.' + file_type
        try:
            if not os.path.isfile(file_path):
                s = requests.Session()
                s.mount(url, HTTPAdapter(max_retries=5))
                downloaded = s.get(url, stream=True, timeout=(5, 10))
                with open(file_path, 'wb') as f:  # w写,b二进制
                    f.write(downloaded.content)
        except Exception as e:
            error_file = self.get_filepath(
                file_type) + os.sep + 'not_downloaded.txt'
            with open(error_file, 'ab') as f:
                url = str(self.order_no) + ':' + file_path + ':' + url + '\n'
                f.write(url.encode(sys.stdout.encoding))
            print(u'文件下载失败: ', e)
            # traceback.print_exc()

    def start(self):
        """运行爬虫"""
        try:
            self.init_config()
            self.get_orders()
            for order in self.orders:
                if self.cookie:
                    order_no = order[0]
                if self.token:
                    order_no = order['orderNo']
                self.initialize_info(order_no)
                self.get_creditors()
            print(u'信息获取完毕，文件保存在此目录： %s ' %
                  (os.path.split(os.path.realpath(__file__))[0] + os.sep + self.date_str))
        except Exception as e:
            print('')
            print(u'错误: ', e)
            # traceback.print_exc()
        finally:
            print('')
            if self.thread and self.thread.is_alive():
                print(u'请按回车键退出...')  # 线程等待输入会影响进程退出
            else:
                input(u'请按回车键退出...')


def main():
    print(u'{}玖富导出工具 v{}{}'.format('-' * 20, 2.0, '-' * 20))
    print('')
    print(u'【使用说明】在谷歌浏览器打开 https://8.9fpuhui.com/login.html 登录成功后，查看是否有持有中的优选出借订单：')
    print(u'若有，先按 F12 打开控制台后再刷新网页，依次点击'
          u'Network -> Name列表中的checkLogin.html -> Headers -> Request Headers，'
          u'复制出Cookie，像这种：[Cookie: cookId=78b***; JSESSIONID=9B2***; logintoken=a01***]；')
    print(u'若没有，则打开 https://m.wukonglicai.com ，先按 F12 打开控制台后再登录，依次点击'
          u'Network -> Name列表中的affirm -> Preview -> 展开data，'
          u'复制出token，像这种：[token: 11223300-4a7ae99fa2b245068588cd963d948a33]。')
    print('')
    if not os.path.isfile('./config.txt'):
        config = input(u'请输入(本窗口标题栏右键 -> 编辑 -> 粘贴)[Cookie/token]：')
    else:
        with open('./config.txt') as f:
            config = f.read()
            print(u'读取到工作目录下的 config.txt 文件。')
    jf = Jiufu(config)
    jf.start()


if __name__ == '__main__':
    main()
