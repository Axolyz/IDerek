# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
# @Author             : Li Baoyan
# @Date               : 2020-01-03 19:19:53
# @Last Modified by   : Li Baoyan
# @Last Modified time : 2020-01-03 19:19:53

from __future__ import with_statement
from __future__ import division
from __future__ import absolute_import
import threading
import time
import Tkinter
import tkMessageBox
import ScrolledText
import urllib2, urllib, urlparse

import bs4
import requests
from io import open


def cut(editor, event=None):
    editor.event_generate(u"<<Cut>>")


def copy(editor, event=None):
    editor.event_generate(u"<<Copy>>")


def paste(editor, event=None):
    editor.event_generate(u"<<Paste>>")


def rightKey(event, editor):
    u"""右键菜单"""
    menubar.delete(0, Tkinter.END)
    menubar.add_command(label=u"剪切", command=lambda: cut(editor))
    menubar.add_command(label=u"复制", command=lambda: copy(editor))
    menubar.add_command(label=u"粘贴", command=lambda: paste(editor))
    menubar.post(event.x_root, event.y_root)


def pack_disposable_widget(widget_args):
    u"""一次性控件打包"""
    if widget_args[0] == u"Label":
        widget = Tkinter.Label(
            widget_args[1],
            text=widget_args[2],
            width=widget_args[3],
            height=widget_args[4],
            wraplength=800,
            justify=u"left",
            font=(u"微软雅黑", 10),
        )
        widget.pack()
        disposable_widgets.add(widget)
    elif widget_args[0] == u"Button":
        widget = Tkinter.Button(
            widget_args[1],
            text=widget_args[2],
            width=widget_args[3],
            height=widget_args[4],
            command=widget_args[5],
            font=(u"微软雅黑", 10),
        )
        widget.pack()
        disposable_widgets.add(widget)
    else:
        raise Exception(u'"pack_disposable_widget()" does not support this widget.')
    return widget


def change_disposable_widget(interface):
    u"""一次性控件转场"""
    for widgets in disposable_widgets:
        widgets.destroy()
    disposable_widgets.clear()
    for widgets in interface:
        pack_disposable_widget(widgets)


def search_html(idiom):  # 最核心部分（然而很弱智
    url = (
        u"https://hanyu.baidu.com/s?wd="
        + urllib.quote(idiom.encode(u"utf8"))
        + u"&ptype=zici"
    )
    response = requests.get(url)
    idiom_html = response.text
    return idiom_html


def keep_chinese(content):
    u"""输入文本，返回所有非中文字符变成空格的文本"""
    contentstr = u""
    for char in content:
        if char >= u"\u4e00" and char <= u"\u9fa5":
            contentstr += char
        else:
            contentstr = contentstr + u" "
    return contentstr


def check_timeout():
    while is_searching:
        time.sleep(5)
        check_time = time.time()
        if check_time - last_search_time > TIMEOUT:
            tkMessageBox.showerror(u"", u"请求超时，请重试，或重启电脑后重试。")
            root.destroy()


def input_word_num():

    num = t.get(u"0.0", u"end").strip()
    t.delete(u"1.0", u"end")

    try:
        word_nums.add(int(num))
        tkMessageBox.showinfo(u"", u"输入成功。若有其他字数类型请继续输入。")
    except ValueError:
        if not num:
            tkMessageBox.showinfo(u"", u"请在输入框内输入字数类型。")
        else:
            tkMessageBox.showwarning(u"", u"请输入纯数字！！")


def to_search_definition():
    if t.get(u"0.0", u"end").strip():
        tkMessageBox.showwarning(u"", u"输入框内仍有待输入的字数类型，请先点击输入！！")
    elif word_nums:
        change_disposable_widget(INTERFACE2)
        tkMessageBox.showinfo(u"", u"请将待查错的成语单OCR（图片转文字）结果置于以上输入框内，不需改格式。")
    else:
        tkMessageBox.showwarning(u"", u"未输入字数类型！！")


def search_definition_gui(function):

    global progress, top

    tkMessageBox.showinfo(u"", u"查错中，请耐心等待……")
    progress = Tkinter.StringVar()
    progress.set(u"完成度：0%")

    top = Tkinter.Toplevel()
    Tkinter.Label(top, text=u"请勿关闭此窗口。", width=20, height=1).pack()
    Tkinter.Label(top, textvariable=progress, width=20, height=3).pack()

    all_input_idiom = t.get(u"0.0", u"end").replace(u"█", u"").strip()

    th1 = threading.Thread(target=function, args=(all_input_idiom,))
    th1.setDaemon(True)
    th1.start()

    wait_until_complete()


def wait_until_complete():

    global all_output_idiom

    if is_searching:
        root.after(500, wait_until_complete)
    else:
        top.destroy()

        t.delete(u"1.0", u"end")
        t.insert(u"1.0", all_output_idiom)

        change_disposable_widget(INTERFACE3)

        if not all_output_idiom:
            tkMessageBox.showinfo(u"", u"请将待查错的成语单OCR（图片转文字）结果置于以上输入框内。")
        elif all_output_idiom.find(u"█") != -1:
            tkMessageBox.showinfo(u"", u"查错已完成。请修改已标记成语的错误。")
        else:
            tkMessageBox.showinfo(u"", u"查错已完成。无错误。")


def search_definition_first_time_threading(all_input_idiom):

    global all_output_idiom, last_search_time, is_searching

    all_output_idiom = u""

    is_searching = True

    idioms = [
        idiom for idiom in keep_chinese(all_input_idiom).split() if idiom
    ]  # 成语文本转列表

    all_count = len(idioms)
    start = time.time()
    last_search_time = time.time()
    searched_count = 0

    th1 = threading.Thread(target=check_timeout)
    th1.setDaemon(True)
    th1.start()

    for idiom in idioms:
        idiom_html = search_html(idiom)
        if idiom_html.find(u'<div class="tab-content">') != -1:
            passage_texts = (
                bs4.BeautifulSoup(idiom_html, u"lxml")
                .find(class_=u"tab-content")
                .find_all(name=u"p")
            )
            output_idiom = (
                idiom
                + u"："
                + u"".join(
                    [passage_text.contents[0].string for passage_text in passage_texts]
                )
                .replace(u" ", u"")
                .replace(u"\n", u"")
            )
        elif idiom in [x.decode() for x in list(SPECIAL_WORDS)]:
            output_idiom = idiom + u"：" + SPECIAL_WORDS[idiom.encode()].decode()
        else:
            output_idiom = u"████" + idiom  # 错误码

        try:
            last_search_time = time.time()
            searched_count += 1
            unsearched_count = all_count - searched_count
            used_time = last_search_time - start
            speed = searched_count / used_time
            rest_time = unsearched_count / speed
            progress.set(
                u"预计剩余时间：{}s\n完成度：{}%\n速度：{}个/s".format(
                    unicode(round(rest_time, 2)),
                    unicode(round(searched_count / all_count * 100, 2)),
                    unicode(round(speed, 2)),
                )
            )
        except ZeroDivisionError:
            searched_count += 1
            progress.set(u"完成度：100%")

        all_output_idiom += output_idiom + u"\n"

    is_searching = False


def search_definition_again_threading(all_input_idiom):

    global all_output_idiom, last_search_time, is_searching

    idioms = [idiom for idiom in all_input_idiom.split() if idiom]

    all_output_idiom = u""

    is_searching = True

    all_count = len(
        [idiom for idiom in idioms if idiom.find(u"：") == -1]
    )  # 没有":"，即没查过的词语总数
    start = time.time()
    last_search_time = time.time()
    searched_count = 0

    th1 = threading.Thread(target=check_timeout)
    th1.setDaemon(True)
    th1.start()

    for idiom in idioms:
        if idiom.find(u"：") != -1:
            output_idiom = idiom
        else:
            idiom = idiom.replace(u"█", u"")
            idiom_html = search_html(idiom)

            if idiom_html.find(u'<div class="tab-content">') != -1:
                passage_texts = (
                    bs4.BeautifulSoup(idiom_html, u"lxml")
                    .find(class_=u"tab-content")
                    .find_all(name=u"p")
                )
                output_idiom = (
                    idiom
                    + u"："
                    + u"".join(
                        [
                            passage_text.contents[0].string
                            for passage_text in passage_texts
                        ]
                    )
                    .replace(u" ", u"")
                    .replace(u"\n", u"")
                )
            elif idiom in [x.decode() for x in list(SPECIAL_WORDS)]:
                output_idiom = idiom + u"：" + SPECIAL_WORDS[idiom.encode()].decode()
            else:
                output_idiom = u"██" + idiom  # 错误码

            try:
                last_search_time = time.time()
                searched_count += 1
                unsearched_count = all_count - searched_count
                used_time = last_search_time - start
                speed = searched_count / used_time
                rest_time = unsearched_count / speed
                progress.set(
                    u"预计剩余时间：{}s\n完成度：{}%\n速度：{}个/s".format(
                        unicode(round(rest_time, 2)),
                        unicode(round(searched_count / all_count * 100, 2)),
                        unicode(round(speed, 2)),
                    )
                )
            except ZeroDivisionError:
                searched_count += 1
                progress.set(u"完成度：100%")

        all_output_idiom += output_idiom + u"\n"

    is_searching = False


def output_definition():

    all_output_idiom_definition = u"\n".join(
        [idiom for idiom in t.get(u"0.0", u"end").strip().split() if idiom]
    )
    all_output_idiom = u"\n".join(
        [
            line.split(u"：")[0] if line.find(u"：") != -1 else line.strip()
            for line in all_output_idiom_definition.split(u"\n")
        ]
    )

    with open(u"成语总集.txt", u"r+", encoding=u"gbk") as all_idiom_file:
        content = all_idiom_file.read()
        all_idiom_file.seek(0, 0)
        all_idiom_file.write(
            unicode(time.strftime(u"%Y-%m-%d %H:%M:%S", time.localtime()))
            + u"\n"
            + all_output_idiom
            + u"\n\n"
            + content
        )
    with open(u"释义总集.txt", u"r+", encoding=u"gbk") as all_definition_file:
        content = all_definition_file.read()
        all_definition_file.seek(0, 0)
        all_definition_file.write(
            unicode(time.strftime(u"%Y-%m-%d %H:%M:%S", time.localtime()))
            + u"\n"
            + all_output_idiom_definition
            + u"\n"
            + content
        )

    tkMessageBox.showinfo(u"", u"成语已自动追加至成语总集.txt中。释义已自动追加至释义总集.txt中。")


def pure_messagebox(text):
    pseudo_root = Tkinter.Tk()
    pseudo_root.withdraw()  # 隐藏主窗口，实现只有一个弹窗弹出
    tkMessageBox.showinfo(u"", text)
    pseudo_root.destroy()  # 销毁假的主窗口


def quit_main():
    pure_messagebox(
        u"感谢使用IDerek。反馈请发送至邮箱792405142@qq.com或github@This-username-is-available。"
    )
    root.destroy()


if __name__ == u"__main__":

    import sys

    reload(sys)
    sys.setdefaultencoding("utf-8")

    is_searching = True
    word_nums = set()
    disposable_widgets = set()
    SPECIAL_WORDS = {
        "\xe4\xb8\x80\xe7\x8f\xad\xe9\x9c\xb8\xe6\xb0\x94": "\xe6\xb0\xb8\xe4\xb9\x85\xe6\xb5\x81\xe4\xbc\xa0",
        "\xe9\xaa\x8c\xe8\xaf\x81\xe9\x97\xae\xe9\xa2\x98\xe7\xad\x94\xe6\xa1\x88": "[0]",
    }
    TIMEOUT = 30

    pure_messagebox(
        u"""欢迎使用IDerek。
    请确定有网络连接。
    请从现在开始认真留意下方提示框中的每一个字！！
    反馈请发送至邮箱792405142@qq.com或github@This-username-is-available。"""
    )

    root = Tkinter.Tk()
    root.title(u"IDerek")
    w, h = root.maxsize()
    root.geometry(u"{}x{}".format(w, h))

    menubar = Tkinter.Menu(root, tearoff=False)
    t = ScrolledText.ScrolledText(root, width=100, height=18, font=(u"微软雅黑", 10))
    t.pack()
    t.bind(u"<Button-3>", lambda x: rightKey(x, t))  # 右键菜单

    INTERFACE3 = (
        (
            u"Button",
            root,
            u"再次查询释义并标记",
            20,
            2,
            lambda: search_definition_gui(search_definition_again_threading),
        ),
        (u"Button", root, u"输出释义至文件", 20, 2, output_definition),
        (u"Button", root, u"退出", 20, 2, quit_main),
        (
            u"Label",
            root,
            u"""有标记的成语需手工改错，改错时更正汉字的错误即可，不需要删去空行和空格以及“█”。要保证每行不能有两个及以上成语。中间有标点的成语应写到一行里并把标点去掉。
    手工改错后再次查询，会把未查询的成语释义查出，如果还有错误可以改正后再查。
    若有某些“█”误标记，很可能是上一步的字数类型输入错误，如果不是请直接输出，后期处理时再加到文件里。""",
            120,
            8,
        ),
    )

    INTERFACE2 = (
        (
            u"Button",
            root,
            u"整理，查询释义并标记",
            20,
            2,
            lambda: search_definition_gui(search_definition_first_time_threading),
        ),
        (
            u"Label",
            root,
            u"""首次查错会将原来杂乱的文本自动整理为每行一个成语+该成语释义的标准格式并用“██”标记查不到或有错误的成语。查错速度与网速正相关。""",
            120,
            8,
        ),
    )

    INTERFACE1 = (
        (u"Button", root, u"点击以输入字数类型", 20, 2, input_word_num),
        (u"Button", root, u"下一环节", 20, 2, to_search_definition),
        (
            u"Label",
            root,
            u"输入字数类型会将输入框中的纯数字作为字数类型输入并清空输入框。例如成语里有四，六，八字成语，那就分三次输入，每次只输入一个纯数字——比如“4”，然后按下按钮，再重复如上步骤分别输入“6”、“8”。输完所有字数类型后再进行下一环节。",
            120,
            8,
        ),
    )

    change_disposable_widget(INTERFACE1)
    root.mainloop()
