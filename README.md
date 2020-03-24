<p align="center"><img src="https://i.loli.net/2020/03/13/ShB1HLiFNCOAW6u.png"  width="100">

# IDerek（语流）

重新定义成语</p>

## 功能

IDerek是一个使用Python开发的小应用，支持关于成语处理的各项操作。

- 成语单OCR结果格式化

- 自动改错

- 批量查询成语或词语释义

- 快捷，便利，自动化，一站式

可以查询（包括但不限于）汉字，词语，术语，成语。

**本项目内不含OCR软件！！只提供对OCR结果的处理！！**

## 依赖

标准版：Windows7+操作系统

对应源码版：Python3.6+和一堆依赖库

xp版：Windows xp+操作系统

对应源码版：Python2.7+和一堆依赖库

## 下载

下载[release](https://github.com/This-username-is-available/IDerek/releases)发布版。

## 使用

运行exe文件，内附GUI及操作指导。

还需要成语单的OCR结果或成语文本，对文本格式几乎无要求。

## 相关

### 原理

通过除逗号外的非汉字字符划分输入的OCR结果来格式化同时允许中间有逗号的成语的存在。

通过百度汉语的（伪）API接口抓取词条页面，百度汉语中能查到的视为正确。

通过在成语数据库中进行相似度比对实现自动改错。

爬取成语数据库的脚本在我的项目[my-baiduhanyu](https://github.com/This-username-is-available/my-baiduhanyu)中，还附带一个爬释义的。

### 关于不同版本

xp版是Windows通用的。但是查词逻辑相当落后，不支持自动改错，错误率较高。而且巨！慢！无！比！。Windows xp只能用这个版本。现已停止更新功能。

标准版只能用在Win7以上操作系统，速度飞快，支持自动改错。

### 权威性

你完全可以把它当成一个快捷版百度汉语。百度汉语权威性还是有保障的，至少比百度百科靠谱。对付高考还是绰绰有余。

没有采用某些现成的开源数据库，一是其中数据有很多错误，二是考虑到时效性。为了权威性和全面性还特意做了很多努力。

### 自定义成语释义

自行改动user_data.json。

### 下一步可能的改进方向

- 行首是否带序号

- 成语之间是否空行

真需要的可以issue或者发邮箱，需要的人多再加入。

关于更加详尽的用法，参见项目内使用说明。

## 作者

- Github：[@This-username-is-available](https://github.com/This-username-is-available)

- 邮箱：<792405142@qq.com>

## 支持

如果这个项目帮到了你，给我个星标吧！

也可以扫这个赞助二维码请我喝杯咖啡哦~

<img src="https://i.loli.net/2020/03/13/83wLpUO7ZJb1qya.jpg"  width="250">

## License

Apache License 2.0

Copyright © 2020 This-username-is-available

**本项目不用于任何商业用途！！侵删！！**
