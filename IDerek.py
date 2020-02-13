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


def cut(editor, event=None):
    editor.event_generate("<<Cut>>")


def copy(editor, event=None):
    editor.event_generate("<<Copy>>")


def paste(editor, event=None):
    editor.event_generate("<<Paste>>")


def rightKey(event, editor):
    """右键菜单"""
    menubar.delete(0, tkinter.END)
    menubar.add_command(label="剪切", command=lambda: cut(editor))
    menubar.add_command(label="复制", command=lambda: copy(editor))
    menubar.add_command(label="粘贴", command=lambda: paste(editor))
    menubar.post(event.x_root, event.y_root)


def pack_disposable_widget(widget_args):
    """一次性控件打包"""
    if widget_args[0] == "Label":
        widget = tkinter.Label(
            widget_args[1],
            text=widget_args[2],
            width=widget_args[3],
            height=widget_args[4],
            wraplength=800,
            justify="left",
        )
        widget.pack()
        disposable_widgets.add(widget)
    elif widget_args[0] == "Button":
        widget = tkinter.Button(
            widget_args[1],
            text=widget_args[2],
            width=widget_args[3],
            height=widget_args[4],
            command=widget_args[5],
        )
        widget.pack()
        disposable_widgets.add(widget)
    else:
        raise Exception('"pack_disposable_widget()" does not support this widget.')
    return widget


def change_disposable_widget(interface):
    """一次性控件转场"""
    for widgets in disposable_widgets:
        widgets.destroy()
    disposable_widgets.clear()
    for widgets in interface:
        pack_disposable_widget(widgets)


def search_html(idiom):
    """输入成语，返回搜索结果页面html"""  # 最核心部分（然而很弱智
    url = "https://hanyu.baidu.com/s?wd=" + str(idiom) + "&ptype=zici"
    url = urllib.parse.quote(url, safe="/:?=")
    response = requests.get(url)
    idiom_html = response.text
    return idiom_html


def keep_chinese(content):
    """输入文本，返回所有非中文字符变成空格的文本"""
    contentstr = ""
    for char in content:
        if char >= u"\u4e00" and char <= u"\u9fa5":
            contentstr += char
        else:
            contentstr = contentstr + " "
    return contentstr


def fmt(input_text):  # 这个函数是为了避过\n在字符串中出现
    idiom = input_text.split()
    output_text = "\n".join(idiom)
    return output_text


def input_word_num():

    num = t.get("0.0", "end").strip()
    t.delete("1.0", "end")

    try:
        word_nums.add(int(num))
        tkinter.messagebox.showinfo("", "输入成功。若有其他字数类型请继续输入。")
    except ValueError:
        if not num:
            tkinter.messagebox.showinfo("", "请在输入框内输入字数类型。")
        else:
            tkinter.messagebox.showwarning("", "请输入纯数字！！")


def to_error_check():
    if t.get("0.0", "end").strip():
        tkinter.messagebox.showwarning("", "输入框内仍有待输入的字数类型，请先点击输入！！")
    elif word_nums:
        change_disposable_widget(INTERFACE2)
        tkinter.messagebox.showinfo("", "请将待查错的成语单OCR（图片转文字）结果置于以上输入框内，不需改格式。")
    else:
        tkinter.messagebox.showwarning("", "未输入字数类型！！")


def error_check_threading():

    start = time.time()
    idioms = []
    all_output_idiom = ""
    searched_count = 0

    all_input_idiom = t.get("0.0", "end").replace("█", "")

    idioms = keep_chinese(all_input_idiom).split()
    all_count = len(idioms)

    for idiom in idioms:
        if idiom in [x.decode() for x in list(SPECIAL_WORDS)] or (
            len(idiom) in word_nums
            and search_html(idiom).find("抱歉：百度汉语中没有收录相关结果。") == -1
        ):
            output_idiom = idiom
        else:
            output_idiom = "██" + idiom

        all_output_idiom += output_idiom + "\n"
        try:
            now = time.time()
            searched_count += 1
            unsearched_count = all_count - searched_count
            used_time = now - start
            speed = searched_count / used_time
            rest_time = unsearched_count / speed

            progress.set(
                "预计剩余时间：{}s\n完成度：{}%\n速度：{}个/s".format(
                    str(round(rest_time, 2)),
                    str(round(searched_count / all_count * 100, 2)),
                    str(round(speed, 2)),
                )
            )
        except ZeroDivisionError:
            searched_count += 1
            progress.set("完成度：100%")

    top.destroy()

    t.delete("1.0", "end")
    t.insert("1.0", all_output_idiom)

    if not all_output_idiom:
        tkinter.messagebox.showinfo("", "请将待查错的成语单OCR（图片转文字）结果置于以上输入框内。")
    elif all_output_idiom.find("█") != -1:
        tkinter.messagebox.showinfo("", "查错已完成。请修改已标记成语的错误。")
    else:
        tkinter.messagebox.showinfo("", "查错已完成。无错误。")


def error_check():

    global progress, top

    tkinter.messagebox.showinfo("", "查错中，请耐心等待……")

    progress = tkinter.StringVar()
    progress.set("完成度：0%")

    top = tkinter.Toplevel()
    tkinter.Label(top, text="请勿关闭此窗口。", width=20, height=1).pack()
    tkinter.Label(top, textvariable=progress, width=20, height=3).pack()

    threading.Thread(target=error_check_threading).start()


def to_search_definition():

    input_text = t.get("0.0", "end").replace("█", "")
    output_text = fmt(input_text)

    t.delete("1.0", "end")
    t.insert("1.0", output_text)

    change_disposable_widget(INTERFACE3)


def search_definition_threading():

    start = time.time()
    idioms = []
    all_output_idiom_definition = ""
    searched_count = 0

    all_input_idiom = t.get("0.0", "end").replace("█", "")

    idioms = all_input_idiom.split()
    all_count = len(idioms)
    all_output_idiom = "\n".join(idioms) + "\n"

    for idiom in idioms:
        if search_html(idiom).find('<div class="tab-content">') != -1:
            bar = (
                bs4.BeautifulSoup(search_html(idiom), "lxml")
                .find(class_="tab-content")
                .find_all(name="p")
            )
            output_idiom_definition = (
                "".join([foo.contents[0].string for foo in bar])
                .replace(" ", "")
                .replace("\n", "")
            )
        elif idiom in [x.decode() for x in list(SPECIAL_WORDS)]:
            output_idiom_definition = SPECIAL_WORDS[idiom.encode()].decode()
        else:
            output_idiom_definition = "████"  # 错误码

        all_output_idiom_definition += idiom + "：" + output_idiom_definition + "\n"
        try:
            now = time.time()
            searched_count += 1
            unsearched_count = all_count - searched_count
            used_time = now - start
            speed = searched_count / used_time
            rest_time = unsearched_count / speed

            progress.set(
                "预计剩余时间：{}s\n完成度：{}%\n速度：{}个/s".format(
                    str(round(rest_time, 2)),
                    str(round(searched_count / all_count * 100, 2)),
                    str(round(speed, 2)),
                )
            )
        except ZeroDivisionError:
            searched_count += 1
            progress.set("完成度：100%")

    top.destroy()

    t.delete("1.0", "end")
    t.insert("1.0", all_output_idiom_definition)

    with open("成语总集.txt", "r+", encoding="gbk") as all_idiom_file:
        content = all_idiom_file.read()
        all_idiom_file.seek(0, 0)
        all_idiom_file.write(
            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            + "\n"
            + all_output_idiom
            + "\n"
            + content
        )
    with open("释义总集.txt", "r+", encoding="gbk") as all_definition_file:
        content = all_definition_file.read()
        all_definition_file.seek(0, 0)
        all_definition_file.write(
            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            + "\n"
            + all_output_idiom_definition
            + "\n"
            + content
        )

    tkinter.messagebox.showinfo("", "释义查询已完成。成语已自动追加至成语总集.txt中。释义已自动追加至释义总集.txt中。")


def search_definition():

    global progress, top

    tkinter.messagebox.showinfo("", "释义查询中，请耐心等待……")

    progress = tkinter.StringVar()
    progress.set("完成度：0%")

    top = tkinter.Toplevel()
    tkinter.Label(top, text="请勿关闭此窗口。", width=20, height=1).pack()
    tkinter.Label(top, textvariable=progress, width=20, height=3).pack()

    threading.Thread(target=search_definition_threading).start()


word_nums = set()
disposable_widgets = set()
SPECIAL_WORDS = {
    b"\xe4\xb8\x80\xe7\x8f\xad\xe9\x9c\xb8\xe6\xb0\x94": b"\xe6\xb0\xb8\xe4\xb9\x85\xe6\xb5\x81\xe4\xbc\xa0",
    b"\xe9\xaa\x8c\xe8\xaf\x81\xe9\x97\xae\xe9\xa2\x98\xe7\xad\x94\xe6\xa1\x88": b"[0]",
}

tk = tkinter.Tk()
tk.withdraw()  # 隐藏主窗口，实现只有一个弹窗弹出
tkinter.messagebox.showinfo(
    "",
    """欢迎使用IDerek。
请确定有网络连接。
请从现在开始认真留意下方提示框中的每一个字！！
反馈请发送至邮箱792405142@qq.com或github@This-username-is-available。""",
)
tk.destroy()  # 销毁假的主窗口

root = tkinter.Tk()  # 真的主窗口，这么做是为了防止主窗口失焦
root.title("IDerek")
w, h = root.maxsize()
root.geometry("{}x{}".format(w, h))

menubar = tkinter.Menu(root, tearoff=False)
t = tkinter.Text(root, height=25)
t.pack()
t.bind("<Button-3>", lambda x: rightKey(x, t))  # 右键菜单

INTERFACE3 = (
    ("Button", root, "查询释义并输出", 20, 2, search_definition),
    ("Button", root, "完成", 20, 2, root.destroy),
    (
        "Label",
        root,
        """查询释义会将每行的成语后追加上该成语的释义。查询速度与网速正相关，约为0.2个/s到5个/s不等，太慢的话请重启电脑再重试。
“████”表示查询不到对应成语释义。""",
        120,
        8,
    ),
)

INTERFACE2 = (
    ("Button", root, "格式化，查错并标记", 20, 2, error_check),
    ("Button", root, "下一环节", 20, 2, to_search_definition),
    (
        "Label",
        root,
        """查错会将原来杂乱的文本自动格式化为每行一个成语的标准格式并用“██”标记错误的成语。查询速度与网速正相关，约为0.2个/s到5个/s不等，实在太慢的话请重启电脑再重试。
有标记的成语需手工改错，改错时更正汉字的错误即可，“██”不用删，也无需删空行和空格。但要保证每行不能有两个及以上成语。中间有标点的成语应写到一行里并把标点去掉。
手工改错后可以直接下一环节，对自己不放心的还可以再次点击查错检查一遍。
若有某些“█”误标记，很可能是上一步的字数类型输入错误，如果不是请直接进行下一环节。""",
        120,
        8,
    ),
)

INTERFACE1 = (
    ("Button", root, "点击以输入字数类型", 20, 2, input_word_num),
    ("Button", root, "下一环节", 20, 2, to_error_check),
    (
        "Label",
        root,
        "输入字数类型会将输入框中的纯数字作为字数类型输入并清空输入框，例如成语里有四，六，八字成语，那就分三次输入，每次只输入一个纯数字——比如“4”，然后按下按钮，再重复如上步骤分别输入“6”、“8”。输完所有字数类型后再进行下一环节。",
        120,
        8,
    ),
)

change_disposable_widget(INTERFACE1)
root.mainloop()

tk = tkinter.Tk()
tk.withdraw()  # 隐藏主窗口，实现只有一个弹窗弹出
tkinter.messagebox.showinfo(
    "", "感谢使用IDerek。反馈请发送至邮箱792405142@qq.com或github@This-username-is-available。"
)
tk.destroy()  # 销毁假的主窗口
