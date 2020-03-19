#!/usr/bin/env python
# coding=utf-8

"""
@Author       : Li Baoyan
@Date         : 2020-02-23 11:37:56
@Github       : https://github.com/This-username-is-available
@LastEditTime : 2020-02-25 12:43:59
@LastEditors  : Li Baoyan
@Description  : 包括成语单OCR结果格式化，自动改错，批量查询成语释义。
"""


import asyncio
import difflib
import json
import sys
import threading
import time
import tkinter
import tkinter.messagebox
import tkinter.scrolledtext

import aiohttp
import bs4
import requests


def is_connected():
    try:
        requests.get("http://www.baidu.com", timeout=5)
        return True
    except:
        return False


def create_file(name):
    with open(name, "a"):
        pass


def keep_chinese(content):  # 输入文本，返回所有非中文字符（除逗号）变成空格的文本
    contentstr = ""
    for char in content:
        if ((char >= u"\u4e00") and (char <= u"\u9fa5")) or char == "," or char == "，":
            contentstr += char
        else:
            contentstr = contentstr + " "
    return contentstr


def correct(idiom):
    advise = difflib.get_close_matches(idiom, ALL_IDIOMS, n=1, cutoff=0)
    return advise[0]


def correct_it(idiom):
    if len(idiom) <= 2:
        corrects[idiom] = idiom
    elif len(idiom) > 2:
        corrects[idiom] = correct(idiom)


def progress_bar(progress, length):
    blank = (
        "|"
        + "█" * int(progress * length)
        + " " * (length - int(progress * length))
        + "|"
    )
    return blank


def update_progress(searched_count):
    try:
        last_search_time = time.time()
        searched_count += 1
        unsearched_count = all_count - searched_count
        used_time = last_search_time - start_searching_time
        speed = searched_count / used_time
        rest_time = unsearched_count / speed
        progress.set(
            "预计剩余时间：{}s\n{}\n{}个/s".format(
                str(int(rest_time)),
                str(progress_bar(searched_count / all_count, 15)),
                str(int(speed)),
            )
        )
    except ZeroDivisionError:
        progress.set(progress_bar(1, 15))


def right_key(event, editor):
    def cut(editor, event=None):
        editor.event_generate("<<Cut>>")

    def copy(editor, event=None):
        editor.event_generate("<<Copy>>")

    def paste(editor, event=None):
        editor.event_generate("<<Paste>>")

    menubar.delete(0, tkinter.END)
    menubar.add_command(label="剪切", command=lambda: cut(editor))
    menubar.add_command(label="复制", command=lambda: copy(editor))
    menubar.add_command(label="粘贴", command=lambda: paste(editor))
    menubar.post(event.x_root, event.y_root)


def pack_disposable_widget(widget_args):  # 一次性控件打包
    if widget_args[0] == "Label":
        widget = tkinter.Label(
            widget_args[1],
            text=widget_args[2],
            width=widget_args[3],
            height=widget_args[4],
            wraplength=800,
            justify="left",
            font=("微软雅黑", 10),
        )
        widget.pack()
        disposable_widgets.append(widget)
    elif widget_args[0] == "Button":
        widget = tkinter.Button(
            widget_args[1],
            text=widget_args[2],
            width=widget_args[3],
            height=widget_args[4],
            command=widget_args[5],
            font=("微软雅黑", 10),
        )
        widget.pack()
        disposable_widgets.append(widget)
    else:
        raise Exception('"pack_disposable_widget()" does not support this widget.')
    return widget


def change_disposable_widget(interface):  # 一次性控件转场
    for widgets in disposable_widgets:
        widgets.destroy()
    disposable_widgets.clear()
    for widgets in interface:
        pack_disposable_widget(widgets)


def get_def(idiom, idiom_html):
    if len(idiom) == 1:
        try:
            pinyins = (
                bs4.BeautifulSoup(idiom_html, "lxml")
                .find(name="div", id="word-header", class_="header-info")
                .find(class_="pronounce", id="pinyin")
                .find_all(name="b")
            )
            passage_texts = (
                bs4.BeautifulSoup(idiom_html, "lxml")
                .find(name="div", class_="content means imeans", id="basicmean-wrapper")
                .find(name="div", class_="tab-content")
                .find_all(name=["p", "dt", "span"])
            )
            passage_texts = pinyins + passage_texts
            a = " ".join(
                [
                    passage_text.contents[0].string.strip()
                    for passage_text in passage_texts
                ]
            ).replace("\n", "")
            return a
        except:
            return False

    else:
        try:
            passage_texts = (
                bs4.BeautifulSoup(idiom_html, "lxml")
                .find(name="div", class_="content means imeans", id="basicmean-wrapper")
                .find(name="div", class_="tab-content")
                .find_all(name=["p", "dt", "span"])
            )
            a = " ".join(
                [
                    passage_text.contents[0].string.strip()
                    for passage_text in passage_texts
                ]
            ).replace("\n", "")
            return a
        except:
            try:
                passage_texts = (
                    bs4.BeautifulSoup(idiom_html, "lxml")
                    .find(name="div", class_="content", id="baike-wrapper")
                    .find(name="div", class_="tab-content")
                    .find_all(name=["p", "dt"])
                )
                a = " ".join(
                    [
                        passage_text.contents[0].string.strip()
                        for passage_text in passage_texts
                    ]
                ).replace("\n", "")
                return a
            except:
                return False


def get_idiom(idiom, idiom_html):
    try:
        a = (
            bs4.BeautifulSoup(idiom_html, "lxml")
            .find(name="div", id="term-header")
            .find(name="strong")
            .string.strip()
            .replace(" ", "")
        )
    except:
        a = idiom
    return a


async def aio_requests(idiom, sem, session):
    global timeouts
    url = "https://hanyu.baidu.com/s"
    params = {"wd": idiom, "ptype": "zici"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    }

    async with sem:
        while True:
            try:
                async with session.get(
                    url, params=params, headers=headers, timeout=30
                ) as resp:
                    idiom_html = await resp.text("utf-8", "ignore")
                timeouts = 0
                break
            except:
                idiom_html = ""
                timeouts += 1
                if timeouts == CONTINUOUS_TIMEOUTS_MAX:
                    tkinter.messagebox.showerror("", "请求超时，请重试，或重启电脑后重试。")
                    root.destroy()
    return idiom_html


async def async_main(idioms, function, pool):
    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(pool)
        tasks = []
        for idiom in idioms:
            task = asyncio.ensure_future(function(sem, idiom, session))
            tasks.append(task)
        a = await asyncio.gather(*tasks)
        return a


async def fetch_for_first_and_again_search(sem, idiom, session):

    global last_search_time, searched_count, timeouts

    if len(idiom) in banned_nums:
        correct_it(idiom)
    elif idiom in SPECIAL_WORDS.keys():
        pass
    else:
        task = asyncio.ensure_future(aio_requests(idiom, sem, session))
        idiom_html = await asyncio.gather(task)
        idiom_html = idiom_html[0]
        if get_def(idiom, idiom_html):
            if get_idiom(idiom, idiom_html) == idiom:
                pass
            else:
                corrects[idiom] = get_idiom(idiom, idiom_html)
        else:
            correct_it(idiom)

    update_progress(searched_count)
    searched_count += 1


async def fetch_for_final_search(sem, idiom, session):

    global last_search_time, searched_count, timeouts

    if len(idiom) in banned_nums:
        output_idiom = idiom + "（请修改此处）"
    elif idiom in SPECIAL_WORDS.keys():
        output_idiom = idiom + "：" + SPECIAL_WORDS[idiom]
    else:
        task = asyncio.ensure_future(aio_requests(idiom, sem, session))
        idiom_html = await asyncio.gather(task)
        idiom_html = idiom_html[0]
        if get_def(idiom, idiom_html):
            output_idiom = idiom + "：" + get_def(idiom, idiom_html)
        else:
            output_idiom = idiom + "（请修改此处）"

    update_progress(searched_count)
    searched_count += 1

    return output_idiom


def search_definition_first_time_threading(all_input_idiom):

    global state, last_search_time, searched_count, all_count, start_searching_time, idioms

    state == "searching"

    idioms = [
        idiom.strip(",").strip("，").replace(",", "，")
        for idiom in keep_chinese(all_input_idiom).split()
        if idiom.strip(",").strip("，")
    ]  # 成语文本格式化后转列表
    all_count = len(idioms)
    start_searching_time = time.time()
    last_search_time = time.time()
    searched_count = 0

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_main(idioms, fetch_for_first_and_again_search, POOL))
    loop.close()

    state = "free"


def search_definition_again_threading(all_input_idiom):

    global all_output_idiom, state, last_search_time, searched_count, all_count, start_searching_time, idioms

    state == "searching"

    foo = [line for line in all_input_idiom.split("\n") if line.find("→") != -1]

    user_corrects = {i.split("→")[0].strip(): i.split("→")[1].strip() for i in foo}
    changed_words = [x for x in user_corrects.values() if x]
    idioms = [
        idiom
        for idiom in idioms
        if idiom not in user_corrects.keys() or user_corrects[idiom]
    ]
    idioms = [
        user_corrects[idiom] if idiom in user_corrects.keys() else idiom
        for idiom in idioms
    ]

    all_count = len(changed_words)
    start_searching_time = time.time()
    last_search_time = time.time()
    searched_count = 0

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        async_main(changed_words, fetch_for_first_and_again_search, POOL)
    )
    loop.close()

    state = "free"


def search_definition_final_threading(all_input_idiom):

    global all_output_idiom, state, last_search_time, searched_count, all_count, start_searching_time, idioms

    state == "searching"

    all_count = len(idioms)
    start_searching_time = time.time()
    last_search_time = time.time()
    searched_count = 0

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    all_output_idiom = "\n".join(
        loop.run_until_complete(async_main(idioms, fetch_for_final_search, POOL))
    )
    loop.close()

    state = "searched"


def search_definition_gui(function, text):

    global progress, progress_top, banned_nums, corrects, state

    corrects = {}
    if not var1.get():
        banned_nums = [1]
    else:
        banned_nums = []

    progress = tkinter.StringVar()
    progress.set(progress_bar(0, 15))

    progress_top = tkinter.Toplevel()
    tkinter.Label(progress_top, text=text, width=20, height=1).pack()
    tkinter.Label(
        progress_top,
        textvariable=progress,
        width=20,
        height=3,
        font=("Courier New", 10),
    ).pack()

    all_input_idiom = text_box.get("0.0", "end").strip()

    Thread_1 = threading.Thread(target=function, args=(all_input_idiom,))
    Thread_1.setDaemon(True)
    Thread_1.start()

    state = "searching"
    wait_until_complete()


def wait_until_complete():

    global all_output_idiom

    if state == "searching":
        root.after(CHECK_INTERVAL * 1000, wait_until_complete)  # 自我调用以实现定时调用效果
    else:
        progress_top.destroy()

        text_box.delete("1.0", "end")

        if corrects:
            all_output_idiom = "\n".join([k + "→" + v for k, v in corrects.items()])
            text_box.insert("1.0", all_output_idiom)
            change_disposable_widget(INTERFACE2)
            tkinter.messagebox.showinfo("", "已完成。请审阅改错建议。")
        elif not idioms:
            tkinter.messagebox.showinfo("", "请将待查询的成语单OCR（图片转文字）结果置于以上输入框内。")
        elif state != "searched":
            search_definition_gui(search_definition_final_threading, "已全部应用。查询释义中。")
        elif state == "searched":
            change_disposable_widget(INTERFACE3)
            text_box.insert("1.0", all_output_idiom)
            if all_output_idiom.find("（请修改此处）") == -1:
                tkinter.messagebox.showinfo("", "查询完毕，无错误。")
            else:
                tkinter.messagebox.showinfo(
                    "", "查询完毕，有错误成语，仍错误的成语会自动在后面加上“（请修改此处）”，方便后期处理，请善用记事本的查找功能。"
                )


def output_definition():

    all_output_idiom_definition = text_box.get("0.0", "end").strip()

    all_output_idiom = "\n".join(
        [
            line.split("：")[0] if line.find("：") != -1 else line.strip()
            for line in all_output_idiom_definition.split("\n")
        ]
    )  # 从释义行提出冒号之前的成语再连接

    create_file("成语总集.txt")
    create_file("释义总集.txt")
    with open("成语总集.txt", "r+", encoding="gbk") as all_idiom_file:
        content = all_idiom_file.read()
        all_idiom_file.seek(0, 0)
        all_idiom_file.write(
            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            + "\n"
            + all_output_idiom
            + "\n\n"
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

    tkinter.messagebox.showinfo("", "导出完毕。")


if __name__ == "__main__":

    state = "searching"
    disposable_widgets = []
    CONTINUOUS_TIMEOUTS_MAX = 30
    CHECK_INTERVAL = 1
    POOL = 10
    corrects = {}

    if not is_connected():
        tkinter.messagebox.showerror("", "检测到网络连接异常，请保证网络状况良好。")
        sys.exit()

    with open("data/idiom.json", "r", encoding="utf-8") as database:
        ALL_IDIOMS = json.load(database)
    with open("data/user_data.json", "r", encoding="utf-8") as user_data:
        SPECIAL_WORDS = json.load(user_data)

    root = tkinter.Tk()
    root.title("IDerek")
    width, height = root.maxsize()
    root.geometry("{}x{}".format(width, height))

    menubar = tkinter.Menu(root, tearoff=False)
    text_box = tkinter.scrolledtext.ScrolledText(
        root, width=100, height=20, font=("微软雅黑", 10)
    )
    text_box.pack()
    text_box.bind("<Button-3>", lambda x: right_key(x, text_box))

    var1 = tkinter.IntVar()
    c1 = tkinter.Checkbutton(root, text="查询单个汉字", variable=var1, onvalue=1, offvalue=0)
    c1.pack()

    INTERFACE3 = (
        ("Button", root, "导出释义至文件", 20, 2, output_definition),
        ("Button", root, "退出", 20, 2, root.destroy),
        (
            "Label",
            root,
            """导出释义会将成语和释义导入程序所在文件夹中的成语总集.txt和释义总集.txt。若文件不存在会自动创建，若存在则会在历史记录上追加。""",
            120,
            8,
        ),
    )
    INTERFACE2 = (
        (
            "Button",
            root,
            "应用改错建议",
            20,
            2,
            lambda: search_definition_gui(
                search_definition_again_threading, "检查改错是否正确中。"
            ),
        ),
        (
            "Button",
            root,
            "跳过余下改错建议",
            20,
            2,
            lambda: search_definition_gui(
                search_definition_final_threading, "已跳过。查询释义中。"
            ),
        ),
        (
            "Label",
            root,
            """改错建议需人工审阅，箭头右侧成语若正确请维持原状，若错误请更改。禁止改动箭头左侧成语。若想删除箭头左侧成语请直接删除右侧成语。
对于某些不知道原型是什么的成语，请善用记事本或word的查找功能然后对照原件。
应用改错会应用审阅后的改错建议并显示错误的改错以供再次审阅。
若有某些正确的改错建议无法应用，请再试一次，还不行直接跳过余下改错建议。""",
            120,
            8,
        ),
    )
    INTERFACE1 = (
        (
            "Button",
            root,
            "整理并自动改错",
            20,
            2,
            lambda: search_definition_gui(
                search_definition_first_time_threading, "整理并自动改错中。"
            ),
        ),
        (
            "Label",
            root,
            """请将待查错的成语单OCR（图片转文字）结果原样置于以上输入框内，不需改动。
首次查询会将原来杂乱的文本自动整理并给出改错建议。""",
            120,
            8,
        ),
    )

    change_disposable_widget(INTERFACE1)
    disposable_widgets.append(c1)
    root.mainloop()
