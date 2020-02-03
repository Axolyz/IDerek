# !/usr/bin/env python3
#  -*- coding: utf-8 -*-
# @Author             : Li Baoyan
# @Date               : 2020-01-03 19:19:53
# @Last Modified by   : Li Baoyan
# @Last Modified time : 2020-01-03 19:19:53

import threading
import time
import tkinter
import tkinter.messagebox
import urllib.parse

import bs4
import requests

VERSION = "1.3"
word_nums = []
disposable_widgets = []


def pack_it(foo):
    """一次性打包"""
    if foo[0] == "Label":
        bar = tkinter.Label(
            foo[1],
            text=foo[2],
            width=foo[3],
            height=foo[4],
            wraplength=800,
            justify="left",
        )
        bar.pack()
        disposable_widgets.append(bar)
    elif foo[0] == "Button":
        bar = tkinter.Button(
            foo[1], text=foo[2], width=foo[3], height=foo[4], command=foo[5]
        )
        bar.pack()
        disposable_widgets.append(bar)
    else:
        tkinter.messagebox.showinfo("", "Oops")
    return bar


def change_interface(interface):
    """一次性控件转场"""
    global disposable_widgets
    for widgets in disposable_widgets:
        widgets.destroy()
    disposable_widgets = []
    for widgets in interface:
        pack_it(widgets)


def search_html(idiom):
    """输入成语输出搜索结果页面html"""
    url = "https://hanyu.baidu.com/s?wd=" + str(idiom) + "&ptype=zici"
    url = urllib.parse.quote(url, safe="/:?=")
    response = requests.get(url)
    idiomhtml = response.text
    return idiomhtml


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u"\u4e00" and uchar <= u"\u9fa5":
        return True
    else:
        return False


def keep_chinese(content):
    """输入文本，保留所有中文字符，非中文字符变成空格"""
    contentstr = ""
    for str in content:
        if is_chinese(str):
            contentstr = contentstr + str
        else:
            contentstr = contentstr + " "
    return contentstr


def fmt(input_text):
    idiom = input_text.split()
    output_text = "\n".join(idiom)
    return output_text


def mark_error(idiom):
    """输入成语，只标记有误成语"""
    if (
        len(idiom) not in word_nums
        or search_html(idiom).find("抱歉：百度汉语中没有收录相关结果。") != -1
    ):
        return "██" + idiom
    else:
        return idiom


def input_word_num():

    num = t.get("0.0", "end").replace("\n", "")
    t.delete("1.0", "end")

    try:
        word_nums.append(int(num))
        tkinter.messagebox.showinfo("", "输入成功。")
    except ValueError:
        if num == "":
            tkinter.messagebox.showinfo("", "请在输入框内输入字数类型。")
        else:
            tkinter.messagebox.showinfo("", "请输入合法指令！！")


def error_check():

    global progress

    start = time.time()
    idioms = []
    output_idiom_text = ""
    count = 0

    input_idiom_text = t.get("0.0", "end").replace("█", "")

    idioms = keep_chinese(input_idiom_text).split()
    all_count = len(idioms)

    for idiom in idioms:
        output_idiom_text += mark_error(idiom) + "\n"  # 成语格式化输出

        now = time.time()
        count += 1
        un_count = all_count - count
        al_time = now - start
        speed = count / al_time
        ex_time = un_count / speed

        progress.set(
            "预计剩余时间：{}s\n完成度：{}%\n速度：{}个/s".format(
                str(round(ex_time, 2)),
                str(round(count / all_count * 100, 2)),
                str(round(speed, 2)),
            )
        )

    top.destroy()

    t.delete("1.0", "end")
    t.insert("1.0", output_idiom_text)

    if output_idiom_text == "":
        tkinter.messagebox.showinfo("", "请将待查错的成语单OCR（图片转文字）结果置于以上输入框内。")
    elif output_idiom_text.find("█") != -1:
        tkinter.messagebox.showinfo("", "查错已完成。请修改已标记成语的错误。")
    else:
        tkinter.messagebox.showinfo("", "查错已完成。无错误。可进行下一环节。")


def search_definition():

    global progress, top

    start = time.time()
    idioms = []
    output_idiom_definition_text = ""
    count = 0

    input_idiom_text = t.get("0.0", "end").replace("█", "")

    idioms = input_idiom_text.split()
    all_count = len(idioms)
    output_idiom_text = "\n".join(idioms) + "\n"

    for idiom in idioms:
        input_idiom_html = search_html(idiom)
        have_content = input_idiom_html.find('<div class="tab-content">')  # 是否有词条

        if have_content != -1:
            bar = (
                bs4.BeautifulSoup(input_idiom_html, "lxml")
                .find(class_="tab-content")
                .find_all(name="p")
            )
            idiom_definition = (
                "".join([foo.contents[0].string for foo in bar])
                .replace(" ", "")
                .replace("\n", "")
            )
        else:
            idiom_definition = "████"  # 错误码

        output_idiom_definition_text += idiom + "：" + idiom_definition + "\n"

        now = time.time()
        count += 1
        un_count = all_count - count
        al_time = now - start
        speed = count / al_time
        ex_time = un_count / speed

        progress.set(
            "预计剩余时间：{}s\n完成度：{}%\n速度：{}个/s".format(
                str(round(ex_time, 2)),
                str(round(count / all_count * 100, 2)),
                str(round(speed, 2)),
            )
        )

    top.destroy()

    t.delete("1.0", "end")
    t.insert("1.0", output_idiom_definition_text)

    with open("成语总集.txt", "r+", encoding="gbk") as all_idiom_file:
        content = all_idiom_file.read()
        all_idiom_file.seek(0, 0)
        all_idiom_file.write(
            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            + "\n"
            + output_idiom_text
            + "\n"
            + content
        )
    with open("释义总集.txt", "r+", encoding="gbk") as all_definition_file:
        content = all_definition_file.read()
        all_definition_file.seek(0, 0)
        all_definition_file.write(
            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            + "\n"
            + output_idiom_definition_text
            + "\n"
            + content
        )

    tkinter.messagebox.showinfo("", "释义查询已完成。成语已自动追加至成语总集.txt中。释义已自动追加至释义总集.txt中。")


def main():

    global root, t, i1, i2, i3

    root = tkinter.Tk()
    root.title("IDerek V{}".format(VERSION))
    w, h = root.maxsize()
    root.geometry("{}x{}".format(w, h))

    t = tkinter.Text(root, height=25)
    t.pack()

    i3 = [
        [
            "Button",
            root,
            "查询释义并输出",
            20,
            2,
            lambda: exec(
                """
global progress, top

tkinter.messagebox.showinfo("", "释义查询中，请耐心等待……")

progress = tkinter.StringVar()
progress.set("完成度：0%")

top = tkinter.Toplevel()
tkinter.Label(top, text = "请勿关闭此窗口。", width = 20, height = 1).pack()
tkinter.Label(top, textvariable = progress, width = 20, height = 3).pack()

th1 = threading.Thread(target = search_definition)
th1.start()
"""
            ),
        ],
        [
            "Button",
            root,
            "完成",
            20,
            2,
            lambda: exec(
                """
tkinter.messagebox.showinfo('', '感谢使用IDerek V{}。反馈请发送至邮箱792405142@qq.com或github@This-username-is-available。'.format(VERSION),)
root.destroy()
"""
            ),
        ],
        [
            "Label",
            root,
            """查询释义会将每行的成语后追加上该成语的释义。查询速度约为0.5s至5s一个成语不等，太慢的话请重启电脑再重试。
“████”表示查询不到对应成语释义。
输入框不支持右键菜单，请善用ctrl+c复制和ctrl+v粘贴。""",
            120,
            8,
        ],
    ]
    i2 = [
        [
            "Button",
            root,
            "格式化，查错并标记",
            20,
            2,
            lambda: exec(
                """
global progress, top

tkinter.messagebox.showinfo("", "查错中，请耐心等待……")

progress = tkinter.StringVar()
progress.set("完成度：0%")

top = tkinter.Toplevel()
tkinter.Label(top, text = "请勿关闭此窗口。", width = 20, height = 1).pack()
tkinter.Label(top, textvariable = progress, width = 20, height = 3).pack()

th1 = threading.Thread(target = error_check)
th1.start()
"""
            ),
        ],
        [
            "Button",
            root,
            "下一环节",
            20,
            2,
            lambda: exec(
                """
input_idiom_text = t.get("0.0", "end").replace("█", "")
output_text = fmt(input_idiom_text)

t.delete("1.0", "end")
t.insert("1.0", output_text)

change_interface(i3)
"""
            ),
        ],
        [
            "Label",
            root,
            """请将待查错的成语单OCR（图片转文字）结果置于以上输入框内，不需改格式。输入框不支持右键菜单，请善用ctrl+c复制和ctrl+v粘贴。
查错会将原来杂乱的文本自动格式化为每行一个成语的标准格式并用“██”标记错误的成语。查错速度约为0.5s至5s一个成语不等，实在太慢的话请重启电脑再重试。
有标记的成语需手工改错，改错时更正汉字的错误即可，“██”不用删，也无需删空行和空格。但要保证每行至多有一个成语。中间有标点的成语应把标点去掉。
手工改错后可以直接下一环节，对自己不放心的还可以再次点击查错检查一遍。
若有某些“█”误标记，很可能是上一步的字数类型输入错误，如果不是请直接进行下一环节。""",
            120,
            8,
        ],
    ]
    i1 = [
        ["Button", root, "点击以输入字数类型", 20, 2, input_word_num],
        [
            "Button",
            root,
            "下一环节",
            20,
            2,
            lambda: exec(
                """
if word_nums != []:
    change_interface(i2)
else:
    tkinter.messagebox.showinfo("", "未输入字数类型！！")
"""
            ),
        ],
        [
            "Label",
            root,
            "在上面的输入框内输入字数类型，例如成语里有四，六，八字成语，那就分三次输入，每次只输入一个纯数字——比如‘4’，然后记！得！按！下！按！钮！！若有其他字数类型请继续输入。输完所有字数类型后再进行下一环节。",
            120,
            8,
        ],
    ]

    change_interface(i1)
    tkinter.messagebox.showinfo(
        "",
        """欢迎使用IDerek V{}。
请确定有网络连接。
请从现在开始认真留意下方提示框中的每一个字！！
反馈请发送至邮箱792405142@qq.com或github@This-username-is-available。""".format(
            VERSION
        ),
    )
    root.mainloop()


main()
