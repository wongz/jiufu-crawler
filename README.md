直接下载对应的exe运行，照着step.jpg图里步骤操作。<br>
悟空理财请参照玖富钱包的操作方式，登录前先打开浏览器控制台。
* [功能](#功能)
* [输出](#输出)
* [实例](#实例)
* [运行环境](#运行环境)
* [使用说明](#使用说明)
  * [下载脚本](#1下载脚本)
  * [安装依赖](#2安装依赖)
  * [程序设置](#3程序设置可选)
  * [运行脚本](#4运行脚本)
  * [按需求修改脚本（可选）](#5按需求修改脚本可选)
  * [定期自动爬取（可选）](#6定期自动爬取可选)
* [如何获取cookie](#如何获取cookie)
* [如何检测cookie是否有效](#如何检测cookie是否有效)

## 功能
爬取持有的出借中订单数据，并将结果信息写入文件。写入信息包括了所有出借订单的所有数据，主要有**订单信息**和**债权信息**两大类，前者包含订单号、产品名称、加入金额、服务期届满时间等等；后者包含借款方、证件号/凭证号、借款用途、借出金额等等，因为内容太多，这里不再赘述，详细内容见[输出](#输出)部分。写入文件类型为**csv文件**。<br>
如果你还需要每个订单的《出借咨询及管理服务协议》、《授权委托、反洗钱及出借风险提示书》、《数字证书申请表及授权委托书》及每个债权的《借款协议》、《担保合同》，可以通过是否下载附件的选择功能。程序也可以实现**定期自动爬取**，具体方法见[定期自动爬取](#6定期自动爬取可选)。在<https://8.9fpuhui.com>看到的出借中的订单才能爬取。

## 输出
- 订单列表：ALL_ORDERS.csv

- 债权列表：ORDER_NO.csv

- 文档（可选）：订单的三种PDF文档放在**ALL_ORDERS**文件夹中；债权的两种PDF文档放在**ORDER_NO**文件夹中。

## 实例
我们可以创建**cookie.txt**文件，文件内容如下：
```
cookId=2d43e501-3583-4f23-b427-3236d16d4e88; JSESSIONID=485720964C3BC3E48195C2EF50A94188; logintoken=b968be43-f11a-497c-8e91-0982ea862e88
```
配置完成后运行程序：
```bash
$ python jiufu.py
```
也可以直接运行程序，按提示输入Cookie。程序会自动生成一个当前日期时间（20200926103000）文件夹，我们本次所爬取的所有信息都被存储在20200926103000文件夹里。过程中会询问是否下载附件，5秒内无操作将默认不下载。选择下载后，PDF 文档会存放在与csv同名的对应文件夹中。

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
程序优先读取**cookie.txt**文件，打开你会看到如下内容：
```
cookId=2d43e501-3583-4f23-b427-3236d16d4e88; JSESSIONID=485720964C3BC3E48195C2EF50A94188; logintoken=b968be43-f11a-497c-8e91-0982ea862e88
```
Cookie一长串字符中上面三个为必需参数，可以按照[如何获取cookie](#如何获取cookie)中的方法，获取cookie。

### 4.运行脚本
大家可以根据自己的运行环境选择运行方式，Linux可以通过
```bash
$ python jiufu.py
```
运行；针对Windows系统，已经制作打包成exe文件，无需Python环境直接双击运行。

### 5.按需求修改脚本（可选）
本部分为可选部分，如果你不需要自己修改代码或添加新功能，可以忽略此部分。<br>
本程序所有代码都位于jiufu.py文件，程序主体是一个Jiufu类，上述所有功能都是通过在main函数调用Jiufu类实现的，默认的调用代码如下：
```python
if not os.path.isfile('./cookie.txt'):
    cookie = input(u'工作目录下无cookie.txt文件，请输入Cookie：')
else:
    with open('./cookie.txt') as f:
        cookie = f.read()
        print(u'读取到工作目录下的cookie.txt文件。')
jf = Jiufu(cookie)
jf.start()
```
用户可以按照自己的需求调用或修改Jiufu类。<br>

**jf.orders**：存储出借中的订单列表，订单包含订单号、产品名称等信息。订单的具体信息如下：
```
- 订单号：如jf.orders[0][0]为第一个订单的订单号；
- 产品名称：如jf.orders[0][1]为第一个订单的产品名称；
- 加入时间：如jf.orders[0][2]为第一个订单的加入时间；
- 加入金额：如jf.orders[0][3]为第一个订单的加入金额；
- 起算回报日期：如jf.orders[0][4]为第一个订单的起算回报日期；
- 参考年回报率：如jf.orders[0][5]为第一个订单的参考年回报率；
- 服务期：如jf.orders[0][6]为第一个订单的服务期；
- 期望服务期满总回报：如jf.orders[0][7]为第一个订单的期望服务期满总回报；
- 服务期届满处理方式：如jf.orders[0][8]为第一个订单的服务期届满处理方式；
- 服务期届满时间：如jf.orders[0][9]为第一个订单的服务期届满时间；
- 剩余天数：如jf.orders[0][10]为第一个订单的剩余天数。
```
**jf.creditors**：存储每一笔订单的债权列表，债权包含借款方、借款金额等信息。第 i 笔债权的具体信息如下：
```
- 序号：jf.creditors[i-1][0]为该债权的序号
- 借款方：jf.creditors[i-1][1]为该债权的借款方
- 证件号/凭证号：
- 借款用途：
- 借出金额：
- 借款合同期限：
- 保单号：
- 协议：
- 担保函：
- appid：
- 经营状况及财务状况：
- 还款能力变化情况：
- 逾期情况：
- 涉讼情况：
- 受行政处罚情况：
- 其他影响还款的重大信息：
- 还款保障措施：
- 交易时剩余未还期数：
- 交易时借款合同是否到期：
- 借款到期后贷后是否在追踪延期还款：
````

### 6.定期自动爬取（可选）
我们可以定期爬取备份。本部分为可选部分，如果不需要可以忽略。思路是**利用第三方软件，如crontab，让程序每隔一段时间运行一次**。

## 如何获取cookie
1.用Chrome打开<https://8.9fpuhui.com/login.html>；<br>
2.输入玖富钱包的用户名、密码，登录成功后会跳转到账户中心；<br>
3.按F12键打开Chrome开发者工具，刷新页面；<br>
4.依此点击Chrome开发者工具中的Network->Name中的checkLogin.html->Headers->Request Headers，"Cookie:"后的值即为我们要找的cookie值，复制即可。<br>
如图所示：
![](https://github.com/wongz/jiufu-crawler/blob/master/step.jpg)

## 如何检测cookie是否有效
如果程序报错提示cookie无效等类似信息，说明cookie无效。若通过文件读取cookie，无效时必须删除此cookie.txt文件或修改其文件内容，程序**优先读取**cookie.txt文件，存在cookie.txt文件就会跳过输入Cookie这一步。

## Denounce
**9F Inc.(NASDAQ:JFU), this company deceives customers, transfers a large number of overdue claims and expired claims to the borrower without the lender's knowledge. The overdue rate exceeds 60%, and the company's shareholders have not responded to queries. The money cannot be returned.**
