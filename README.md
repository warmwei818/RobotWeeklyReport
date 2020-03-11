# RobotWeeklyReport

<a name="56glm"></a>
### 背景
公司内部文档使用语雀，我们大部门LD要写周报，各小组TL也要写周报，之前每次周报LD自己汇总，可能要花费半天的时间。由于语雀是基于Markdown格式的, 可以通过语雀API获取MD格式的内容，鉴于大家周报的格式都一致，所以可以很方便进行文档的拆分和合并。于是后边周报就比较省力了，每周末晚上20:00jenkins自动执行下脚本即可生成汇总的周报，然后发送消息到钉钉群里，有需要也可以加上自动发送邮件。emmmm ~~   面向领导编程~~~

真实的周报内容是比较多的，这里的demo，就简写了。

<a name="TXjzy"></a>
### 小组周报

- 格式
![此处输入图片的描述][1]



- MD内容
  ![此处输入图片的描述][2]

<a name="YHlg0"></a>
### 汇总后周报
![此处输入图片的描述][3]

![此处输入图片的描述][4]

<a name="X4bna"></a>
### 钉钉消息
![此处输入图片的描述][5]
<a name="dsVcH"></a>
###
<a name="rxFnE"></a>
### 配置数据
在config_test.ini文件中，有些配置数据。

- api_host=https://www.yuque.com/api/v2/                   语雀API的域名
- report_doc_id=1327538                                    汇总后文档的doc_id
- repo_id=226643                                           知识库的id
- yuque_token=iRa0bHQGIqhK2pgmotiWjXGdIq4T1dmyPK9kByC3     yuque账号的token
- user_agent=SoucheBot                                     ua
- repo_namespace=xuzhenwei/urcgc7                          文档所在工作空间
- dingding_access_token=xx                                 钉钉机器人的token


  [1]: https://cdn.nlark.com/yuque/0/2020/png/148878/1583895359347-53b7e3fc-1e58-404e-a13c-637e4a688cdb.png?x-oss-process=image/resize,w_433
  [2]: https://cdn.nlark.com/yuque/0/2020/png/148878/1583895413082-10f7af66-4777-4dff-b0c8-b549b735cba2.png?x-oss-process=image/resize,w_349
  [3]: https://cdn.nlark.com/yuque/0/2020/png/148878/1583895485049-2477adb6-bf16-42e4-b0cd-f128805ba829.png?x-oss-process=image/resize,w_746
  [4]: https://cdn.nlark.com/yuque/0/2020/png/148878/1583895498580-65dc9ab3-ba32-45cb-a2cc-d6707a7b5fc1.png?x-oss-process=image/resize,w_746
  [5]: https://cdn.nlark.com/yuque/0/2020/png/148878/1583896219852-0a2fa9a7-104d-428c-9a09-ed34b95df358.png?x-oss-process=image/resize,w_746