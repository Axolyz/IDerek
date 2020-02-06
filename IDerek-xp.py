#  -*- coding: utf-8 -*-
# @Author             : Li Baoyan
# @Date               : 2020-01-03 19:19:53
# @Last Modified by   : Li Baoyan
# @Last Modified time : 2020-01-03 19:19:53

import sys
import time
import Tkinter as tk
import urllib

import requests
from bs4 import BeautifulSoup

import tkMessageBox as messagebox

word_nums = []
disposable_widgets = []


def pack_it(a):
    """一次性打包"""
    if a[0] == "Label":
        c = tk.Label(
            a[1], text=a[2], width=a[3], height=a[4], wraplength=800, justify="left"
        )
        c.pack()
        disposable_widgets.append(c)
    elif a[0] == "Button":
        c = tk.Button(a[1], text=a[2], width=a[3], height=a[4], command=a[5])
        c.pack()
        disposable_widgets.append(c)
    elif a[0] == "Toplevel":
        c = tk.Toplevel()
        c.geometry(a[1])
    else:
        messagebox.showinfo("", "Oops")
    return c


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
    url = urllib.quote(url, safe="/:?=")
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
        messagebox.showinfo("", "输入成功。")
    except ValueError:
        if num == "":
            messagebox.showinfo("", "请在输入框内输入字数类型。")
        else:
            messagebox.showinfo("", "请输入合法指令！！")


def error_check():
    messagebox.showinfo("", "查错中，请耐心等待……")

    idioms = []
    output_idiom_text = ""

    input_idiom_text = t.get("0.0", "end").replace("█", "")

    idioms = keep_chinese(input_idiom_text).split()
    output_idiom_text = "\n".join([mark_error(x) for x in idioms])

    t.delete("1.0", "end")
    t.insert("1.0", output_idiom_text)

    if output_idiom_text == "":
        messagebox.showinfo("", "请将待查错的成语单OCR（图片转文字）结果置于以上输入框内。")
    elif output_idiom_text.find("█") != -1:
        messagebox.showinfo("", "查错已完成。请修改已标记成语的错误。")
    else:
        messagebox.showinfo("", "查错已完成。无错误。可进行下一环节。")


def search_definition():
    messagebox.showinfo("", "释义查询中，请耐心等待……")

    idioms = []
    output_idiom_definition_text = ""

    input_idiom_text = t.get("0.0", "end").replace("█", "")

    idioms = input_idiom_text.split()
    output_idiom_text = "\n".join(idioms) + "\n"

    for idiom in idioms:
        input_idiom_html = search_html(idiom)
        have_content = input_idiom_html.find('<div class="tab-content">')  # 是否有词条

        if have_content != -1:
            a = (
                BeautifulSoup(input_idiom_html, "lxml")
                .find(class_="tab-content")
                .find_all(name="p")
            )
            idiom_definition = (
                "".join([x.contents[0].string for x in a])
                .replace(" ", "")
                .replace("\n", "")
            )
        else:
            idiom_definition = "████"  # 错误码

        output_idiom_definition_text += idiom + "：" + idiom_definition + "\n"

    t.delete("1.0", "end")
    t.insert("1.0", output_idiom_definition_text)

    with open(u"成语总集.txt", "r+") as all_idiom_file:
        content = all_idiom_file.read().decode("gbk")
        all_idiom_file.seek(0, 0)
        all_idiom_file.write(
            (
                str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                + "\n"
                + output_idiom_text
                + "\n"
                + content
            ).encode("gbk")
        )
    with open(u"释义总集.txt", "r+") as all_definition_file:
        content = all_definition_file.read().decode("gbk")
        all_definition_file.seek(0, 0)
        all_definition_file.write(
            (
                str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                + "\n"
                + output_idiom_definition_text
                + "\n"
                + content
            ).encode("gbk")
        )

    messagebox.showinfo("", "释义查询已完成。成语已自动追加至成语总集.txt中。释义已自动追加至释义总集.txt中。")


def f1():
    if word_nums != []:
        change_interface(i2)
    else:
        messagebox.showinfo("", "未输入字数类型！！")


def f2():
    input_idiom_text = t.get("0.0", "end").replace("█", "")
    output_text = fmt(input_idiom_text)
    t.delete("1.0", "end")
    t.insert("1.0", output_text)
    change_interface(i3)


def f3():
    messagebox.showinfo(
        "", "感谢使用IDerek。反馈请发送至邮箱792405142@qq.com或github@This-username-is-available。"
    ),
    window.destroy()


def main_interface():
    global window, t, i1, i2, i3

    reload(sys)
    sys.setdefaultencoding("utf-8")

    window = tk.Tk()
    window.title("IDerek")
    w, h = window.maxsize()
    window.geometry("{}x{}".format(w, h))

    t = tk.Text(window, height=30)
    t.pack()

    i3 = [
        ["Button", window, "查询释义并输出", 20, 2, search_definition],
        ["Button", window, "完成", 20, 2, f3],
        [
            "Label",
            window,
            """查询释义会将每行的成语后追加上该成语的释义，中途会伪卡死且没有任何提醒，请耐心等待。查询速度约为0.5s至5s一个成语不等，太慢的话请重启电脑再重试。
“████”表示查询不到对应成语释义。
输入框不支持右键菜单，请善用ctrl+c复制和ctrl+v粘贴。""",
            120,
            8,
        ],
    ]
    i2 = [
        ["Button", window, "格式化，查错并标记", 20, 2, error_check],
        ["Button", window, "下一环节", 20, 2, f2],
        [
            "Label",
            window,
            """请将待查错的成语单OCR（图片转文字）结果置于以上输入框内，不需改格式。输入框不支持右键菜单，请善用ctrl+c复制和ctrl+v粘贴。
查错会将原来杂乱的文本自动格式化为每行一个成语的标准格式并用“██”标记错误的成语，中途会伪卡死且没有任何提醒，请耐心等待。查错速度约为0.5s至5s一个成语不等，实在太慢的话请重启电脑再重试。
有标记的成语需手工改错，改错时更正汉字的错误即可，“██”不用删，也无需删空行和空格。但要保证每行至多有一个成语。中间有标点的成语应把标点去掉。
手工改错后可以直接下一环节，对自己不放心的还可以再次点击查错检查一遍。
若有某些“█”误标记，很可能是上一步的字数类型输入错误，如果不是请直接进行下一环节。""",
            120,
            8,
        ],
    ]
    i1 = [
        ["Button", window, "点击以输入字数类型", 20, 2, input_word_num],
        ["Button", window, "下一环节", 20, 2, f1],
        [
            "Label",
            window,
            "在上面的输入框内输入字数类型，比如我的成语里有四，六，八字成语，那就分三次输入，每次只输入一个纯数字——比如‘4’，然后记！得！按！下！按！钮！！若有其他字数类型请继续输入。输完所有字数类型后再进行下一环节。",
            120,
            8,
        ],
    ]

    change_interface(i1)
    messagebox.showinfo(
        "",
        """欢迎使用IDerek。
请确定有网络连接。
请从现在开始认真留意下方提示框中的每一个字！！
反馈请发送至邮箱792405142@qq.com或github@This-username-is-available。""",
    )
    window.mainloop()


main_interface()
