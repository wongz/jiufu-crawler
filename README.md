* [功能](#功能)
* [输出](#输出)
* [实例](#实例)
* [运行环境](#运行环境)
* [使用说明](#使用说明)
  * [下载脚本](#1下载脚本)
  * [安装依赖](#2安装依赖)
  * [程序设置](#3程序设置)
  * [运行脚本](#4运行脚本)
  * [按需求修改脚本（可选）](#6按需求修改脚本可选)
  * [定期自动爬取（可选）](#7定期自动爬取微博可选)
* [如何获取user_id](#如何获取user_id)
* [添加cookie与不添加cookie的区别（可选）](#添加cookie与不添加cookie的区别可选)
* [如何获取cookie（可选）](#如何获取cookie可选)
* [如何检测cookie是否有效（可选）](#如何检测cookie是否有效可选)

## 功能
连续爬取**一个**或**多个**新浪微博用户（如[Dear-迪丽热巴](https://weibo.cn/u/1669879400)、[郭碧婷](https://weibo.cn/u/1729370543)）的数据，并将结果信息写入文件。写入信息几乎包括了用户微博的所有数据，主要有**用户信息**和**微博信息**两大类，前者包含用户昵称、关注数、粉丝数、微博数等等；后者包含微博正文、发布时间、发布工具、评论数等等，因为内容太多，这里不再赘述，详细内容见[输出](#输出)部分。具体的写入文件类型如下：
- 写入**csv文件**（默认）
<br>

如果你只对用户信息感兴趣，而不需要爬用户的微博，也可以通过设置实现只爬取微博用户信息的功能。程序也可以实现**爬取结果自动更新**，即：现在爬取了目标用户的微博，几天之后，目标用户可能又发新微博了。通过设置，可以实现每隔几天**增量爬取**用户这几天发的新微博。具体方法见[定期自动爬取微博](#7定期自动爬取微博可选)。<br>

## 输出
**用户信息**<br>
- 用户id：微博用户id，如"1669879400"
- 认证信息：为认证用户特有，用户信息栏显示的认证信息
***
**微博信息**<br>
- 微博id：微博的id，为一串数字形式

## 实例
以爬取为例，我们需要修改**cookie.txt**文件，文件内容如下：
```
cookId=2d43e501-3583-4f23-b427-3236d16d4e88; JSESSIONID=485720964C3BC3E48195C2EF50A94188; logintoken=b968be43-f11a-497c-8e91-0982ea862e88
```

配置完成后运行程序：
```bash
$ python jiufu.py
```
程序会自动生成一个当期日期时间（20200926103000）文件夹，我们本次所爬取的所有信息都被存储在20200926103000文件夹里。<br>
**csv文件结果如下所示：**
![](https://picture.cognize.me/cognize/github/weibo-crawler/weibo_csv.png)*1669879400.csv*<br>
本csv文件是爬取的结果文件。<br>

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
下面讲解每个参数的含义与设置方法。<br>
**设置cookie**<br>
```
your cookie
```
如果想要设置cookie，可以按照[如何获取cookie](#如何获取cookie可选)中的方法，获取cookie，并将上面的"your cookie"替换成真实有效的cookie即可。<br>

### 4.运行脚本
大家可以根据自己的运行环境选择运行方式，Linux可以通过
```bash
$ python jiufu.py
```
运行;
### 5.按需求修改脚本（可选）
本部分为可选部分，如果你不需要自己修改代码或添加新功能，可以忽略此部分。<br>
本程序所有代码都位于jiufu.py文件，程序主体是一个Jiufu类，上述所有功能都是通过在main函数调用Jiufu类实现的，默认的调用代码如下：
```python
if not os.path.isfile('././cookie.txt'):
    cookie = input(u'工作目录下无cookie.txt文件，请输入Cookie：')
else:
    with open('./cookie.txt') as f:
        cookie = f.read()
        print(u'读取到工作目录下的cookie.txt文件。')
jf = Jiufu(cookie)
jf.start()
```
用户可以按照自己的需求调用或修改Jiufu类。<br>

**jf.creditors**：存储爬取到的所有债权信息；<br>
jf.creditors包含爬取到的所有债权信息，如**借款人**、**借款金额**等。wb.weibo是一个列表，包含了爬取的所有微博信息。wb.weibo[0]为爬取的第一条微博，wb.weibo[1]为爬取的第二条微博，以此类推。wb.weibo[0]['id']为第一条微博的id，wb.weibo[0]['text']为第一条微博的正文，wb.weibo[0]['created_at']为第一条微博的发布时间，还有其它很多信息不在赘述，大家可以点击下面的"详情"查看具体用法。
<details>
  
<summary>详情</summary>

**user_id**：存储微博用户id。如wb.weibo[0]['user_id']为最新一条微博的用户id；<br>
**screen_name**：存储微博昵称。如wb.weibo[0]['screen_name']为最新一条微博的昵称；<br>
**id**：存储微博id。如wb.weibo[0]['id']为最新一条微博的id；<br>
**text**：存储微博正文。如wb.weibo[0]['text']为最新一条微博的正文；<br>
<details>
  
<summary>详情</summary>

假设爬取到的第i条微博为转发微博，则它存在以下信息：<br>
**user_id**：存储原始微博用户id。wb.weibo[i-1]['retweet']['user_id']为该原始微博的用户id；<br>
**at_users**：存储原始微博@的用户。wb.weibo[i-1]['retweet']['at_users']为该原始微博@的用户，若该原始微博没有@的用户，则值为''。<br>

</details>

</details>

### 7.定期自动爬取（可选）
我们爬取了微博以后，很多微博账号又可能发了一些新微博，定期自动爬取微博就是每隔一段时间自动运行程序，自动爬取这段时间产生的新微博（忽略以前爬过的旧微博）。本部分为可选部分，如果不需要可以忽略。<br>
思路是**利用第三方软件，如crontab，让程序每隔一段时间运行一次**。

## 如何获取cookie（可选）
1.用Chrome打开<https://8.9fpuhui.com/login.html>；<br>
2.输入玖富钱包的用户名、密码，登录，如图所示：
![](https://picture.cognize.me/cognize/github/weibospider/cookie1.png)
登录成功后会跳转到<https://8.9fpuhui.com>;<br>
3.按F12键打开Chrome开发者工具，刷新页面后会显示如下类似界面:
![](https://picture.cognize.me/cognize/github/weibospider/cookie2.png)
4.依此点击Chrome开发者工具中的Network->Name中的weibo.cn->Headers->Request Headers，"Cookie:"后的值即为我们要找的cookie值，复制即可，如图所示：
![](https://picture.cognize.me/cognize/github/weibospider/cookie3.png)

## 如何检测cookie是否有效
1.无cookie.txt文件，运行程序提示输入Cookie，粘贴进去，如果程序报错提示cookie无效等类似信息，说明cookie无效，否则cookie是有效的；<br>
2.将获取的cookie填到cookie.txt文件中，运行程序。如果程序提示cookie无效等相关信息，说明cookie无效，否则cookie是有效的。<br>
**无效必须删除此文件或修改内容，程序优先读取cookie.txt文件，读到文件就跳过输入这一步**。
