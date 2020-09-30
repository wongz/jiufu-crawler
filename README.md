普通用户请直接下载<玖富导出工具v.2.0.exe>直接运行，按使用说明进行操作。
* [功能](#功能)
* [输出](#输出)
* [实例](#实例)
* [运行环境](#运行环境)
* [使用说明](#使用说明)
  * [下载脚本](#1下载脚本)
  * [安装依赖](#2安装依赖)
  * [程序设置](#3程序设置可选)
  * [运行脚本](#4运行脚本)
 *[操作图示](#操作图示)
* [如何获取cookie](#如何获取cookie)
* [如何获取token](#如何获取token)

## 功能
爬取持有的出借中订单数据，并将结果信息写入文件。写入信息包括了所有出借订单的所有数据，主要有**订单信息**和**债权信息**两大类，前者包含订单号、产品名称、加入金额、服务期届满时间等等；后者包含借款方、证件号/凭证号、借款用途、借出金额等等。写入文件类型为**csv文件**。<br>
如果你还需要每个订单的《出借咨询及管理服务协议》、《授权委托、反洗钱及出借风险提示书》、《数字证书申请表及授权委托书》及每个债权的《借款协议》、《担保合同》，可以通过是否下载附件的选择功能。

## 输出
- 订单列表：ALL_ORDERS.csv

- 债权列表：ORDER_NO.csv

- 文档（可选）：PDF文档放在**PDF**文件夹中

## 实例
我们可以创建**config.txt**文件，文件内容如下：
- 玖富普惠
```
cookId=2d43e501-3583-4f23-b42******e88; JSESSIONID=485720964********95C2EF50A94188; logintoken=b968be43-f11a-4******0982ea862e88
```
- 悟空理财
```
token:  "BB123456-4a7ae8dfa2b*********963d948ab0"
```
配置完成后运行程序：
```bash
$ python jiufu.py
```
也可以直接运行程序，按提示输入。程序会自动生成一个当前日期时间（20200926103000）文件夹，我们本次所爬取的所有信息都被存储在20200926103000文件夹里。csv导出结束后会询问是否下载附件。

## 运行环境
- 开发语言：Python3
- 系统： Windows/Linux/macOS

## 使用说明
### 1.下载脚本
```bash
$ git clone https://github.com/wongz/jiufu-crawler.git
```
运行上述命令，将本项目下载到当前目录，如果下载成功当前目录会出现一个名为"jiufu-crawler"的文件夹；
### 2.安装依赖
```bash
$ pip install -r requirements.txt
```
### 3.程序设置（可选）
程序优先读取**config.txt**文件。
玖富普惠使用Cookie，悟空理财使用token。

### 4.运行脚本
大家可以根据自己的运行环境选择运行方式，Linux可以通过
```bash
$ python jiufu.py
```
运行；针对Windows系统，已经制作打包成exe文件，无需Python环境直接双击运行。
担保函下载会触发服务器的反爬机制，下载失败的文件列表保存在PDF文件下的not_downloaded.txt中。

###操作图示
![](https://github.com/wongz/jiufu-crawler/blob/master/step.jpg)

## 如何获取cookie
1.用Chrome打开<https://8.9fpuhui.com/login.html>；<br>
2.输入玖富钱包的用户名、密码，登录成功后会跳转到账户中心；<br>
3.按F12键打开Chrome开发者工具，刷新页面；<br>
4.依此点击Chrome开发者工具中的Network -> Name中的checkLogin.html -> Headers -> Request Headers，"Cookie:"后的值即为我们要找的cookie值，复制即可。<br>

## 如何获取token
1.用Chrome打开<https://m.wukonglicai.com>；<br>
2.按F12键打开Chrome开发者工具；<br>
3.输入悟空理财的用户名、密码，登录；<br>
4.依此点击Chrome开发者工具中的Network -> Name中的affrim -> Preview -> 展开data，"token:"后的值即为我们要找的token值，复制即可。<br>

## Denounce
**9F Inc.(NASDAQ:JFU), this company deceives customers, transfers a large number of overdue claims and expired claims to the borrower without the lender's knowledge. The overdue rate exceeds 60%, and the company's shareholders have not responded to queries. The money cannot be returned.**
