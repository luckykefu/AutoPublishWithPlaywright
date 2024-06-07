import asyncio
import os
import threading
import tkinter as tk
from functools import partial
from publish_func import baijiahao, bilibili, csdn, get_cover, init_browser, jianshu, juejin, tencentcloud, toutiao, wxgzh, zhihu
from playwright.async_api import Playwright, async_playwright, expect

async def run_wxgzh():
    async with async_playwright() as p:
        await wxgzh(p)
        
async def run_bilibili():
    async with async_playwright() as p:
        
        await bilibili(p)

async def run_csdn():
    async with async_playwright() as p:
        
        await csdn(p)

async def run_jianshu():
    async with async_playwright() as p:
        
        await jianshu(p)

async def run_juejin():
    async with async_playwright() as p:
        
        await juejin(p)

async def run_tencentcloud():
    async with async_playwright() as p:
        
        await tencentcloud(p)

async def run_toutiao():
    async with async_playwright() as p:
        await toutiao(p)
        
async def run_zhihu():
    async with async_playwright() as p:
        await zhihu(p)

async def run_baijiahao():
    async with async_playwright() as p:
        
        await baijiahao(p)
        
# 异步事件循环
loop = asyncio.get_event_loop()
# 启动异步函数的新方法
def run_async(async_func):
    def run():
        asyncio.run(async_func())
    threading.Thread(target=run).start()
          
# 创建主窗口
root = tk.Tk()
root.geometry("400x300")

# 创建按钮并绑定对应的函数
button1 = tk.Button(root, text="WZGZH", command=partial(run_async, run_wxgzh))
button1.pack()

button2 = tk.Button(root, text="BaiJiaHao", command=partial(run_async, run_baijiahao))
button2.pack()

button3 = tk.Button(root, text="blbl", command=partial(run_async, run_bilibili))
button3.pack()

button4 = tk.Button(root, text="csdn", command=partial(run_async, run_csdn))
button4.pack()

button5 = tk.Button(root, text="jianshu", command=partial(run_async, run_jianshu))
button5.pack()

button6 = tk.Button(root, text="juejin", command=partial(run_async, run_juejin))
button6.pack()

button7 = tk.Button(root, text="tencentcloud", command=partial(run_async, run_tencentcloud))
button7.pack()

button8 = tk.Button(root, text="toutiao", command=partial(run_async, run_toutiao))
button8.pack()

button9 = tk.Button(root, text="zhihu", command=partial(run_async, run_zhihu))
button9.pack()

# 运行应用程序
root.mainloop()
