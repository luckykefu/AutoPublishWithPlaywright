import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
import json
import os
from functools import partial
import asyncio
from publish_func import md2copy, baijiahao, bilibili, csdn,init_browser, jianshu, juejin, tencentcloud, toutiao, wxgzh, zhihu
import threading
import tkinter.font as tkFont


DATA_FILE = "last_publish_data.json"

class ArticlePublisher(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        
        self.title("Article Publisher")
        self.geometry("800x600")

        # 使用支持中文的字体
        self.default_font = tkFont.nametofont("TkDefaultFont")
        self.default_font.configure(family="Microsoft YaHei", size=10)  # SimHei (黑体) 是一个常见的中文字体
        self.option_add("*Font", self.default_font)

        self.saved_data = self.load_data()

        # 配置 grid 的列宽度比例
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)


        # Left column
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Title
        self.title_label = ttk.Label(left_frame, text="Title")
        self.title_label.grid(row=0, column=0, pady=5, sticky="e")
        self.title_entry = ttk.Entry(left_frame, width=30)
        self.title_entry.grid(row=0, column=1, pady=5)


        # Description
        self.description_label = ttk.Label(left_frame, text="Description")
        self.description_label.grid(row=1, column=0, pady=5, sticky="e")
        self.description_entry = ttk.Entry(left_frame, width=30)
        self.description_entry.grid(row=1, column=1, pady=5)

        # Tags
        self.tags_label = ttk.Label(left_frame, text="Tags")
        self.tags_label.grid(row=2, column=0, pady=5, sticky="e")
        self.tags_entry = ttk.Entry(left_frame, width=30)
        self.tags_entry.grid(row=2, column=1, pady=5)

        # Cover Images
        self.cover_label = ttk.Label(left_frame, text="Cover Images")
        self.cover_label.grid(row=3, column=0, pady=5, sticky="e")
        self.cover_button = ttk.Button(left_frame, text="Upload Images", command=self.upload_images, bootstyle="primary")
        self.cover_button.grid(row=3, column=1, pady=5)
        self.cover_path = tk.StringVar()
        self.cover_entry = ttk.Entry(left_frame, textvariable=self.cover_path, state='readonly', width=30)
        self.cover_entry.grid(row=4, column=1, pady=5)

        # File URL
        self.file_label = ttk.Label(left_frame, text="File URL")
        self.file_label.grid(row=5, column=0, pady=5, sticky="e")
        self.file_button = ttk.Button(left_frame, text="Upload File", command=self.upload_file, bootstyle="primary")
        self.file_button.grid(row=5, column=1, pady=5)
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(left_frame, textvariable=self.file_path, state='readonly', width=30)
        self.file_entry.grid(row=6, column=1, pady=5)

        # md 转换 url (MD Conversion URL)
        self.md_conv_label = ttk.Label(left_frame, text="MD2Copy URL")
        self.md_conv_label.grid(row=7, column=0, pady=5, sticky="e")
        self.md_conv_entry = ttk.Entry(left_frame, width=30)
        self.md_conv_entry.grid(row=7, column=1, pady=5)
        # Author
        self.author_label = ttk.Label(left_frame, text="Author")
        self.author_label.grid(row=8, column=0, pady=5, sticky="e")
        self.author_entry = ttk.Entry(left_frame, width=30)
        self.author_entry.grid(row=8, column=1, pady=5)

        # Right column
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.platform_label = ttk.Label(right_frame, text="Publish Platforms",  bootstyle="info")
        self.platform_label.grid(row=0, column=0, pady=5, sticky="w")
        # Additional buttons for different platforms

        self.copyMD_button = ttk.Button(right_frame, text="Copy MD to Clipboard", command=self.copy_md_to_clipboard, bootstyle="info")
        self.copyMD_button.grid(row=1, column=0, pady=5, sticky="w")

        self.wzgzh_button = ttk.Button(right_frame, text="Publish to WZGZH", command=self.publish_wxgzh, bootstyle="success")
        self.wzgzh_button.grid(row=5, column=0, pady=5, sticky="w")

        self.baijiahao_button = ttk.Button(right_frame, text="Publish to BaiJiaHao", command=self.publish_baijiahao, bootstyle="success")
        self.baijiahao_button.grid(row=6, column=0, pady=5, sticky="w")

        # self.bilibili_button = ttk.Button(right_frame, text="Publish to blbl", command=partial(self.run_async, self.run_bilibili), bootstyle="success")
        # self.bilibili_button.grid(row=7, column=0, pady=5, sticky="w")

        # self.csdn_button = ttk.Button(right_frame, text="Publish to csdn", command=partial(self.run_async, self.run_csdn), bootstyle="success")
        # self.csdn_button.grid(row=8, column=0, pady=5, sticky="w")

        # self.jianshu_button = ttk.Button(right_frame, text="Publish to jianshu", command=partial(self.run_async, self.run_jianshu), bootstyle="success")
        # self.jianshu_button.grid(row=9, column=0, pady=5, sticky="w")

        # self.juejin_button = ttk.Button(right_frame, text="Publish to juejin", command=partial(self.run_async, self.run_juejin), bootstyle="success")
        # self.juejin_button.grid(row=10, column=0, pady=5, sticky="w")

        # self.tencentcloud_button = ttk.Button(right_frame, text="Publish to tencentcloud", command=partial(self.run_async, self.run_tencentcloud), bootstyle="success")
        # self.tencentcloud_button.grid(row=11, column=0, pady=5, sticky="w")

        self.toutiao_button = ttk.Button(right_frame, text="Publish to toutiao", command=self.publish_toutiao, bootstyle="success")
        self.toutiao_button.grid(row=12, column=0, pady=5, sticky="w")

        self.zhihu_button = ttk.Button(right_frame, text="Publish to zhihu", command=self.publish_zhihu, bootstyle="success")
        self.zhihu_button.grid(row=13, column=0, pady=5, sticky="w")

        self.save_data_button = ttk.Button(right_frame, text="Save Data", command=self.save_data, bootstyle="info")
        self.save_data_button.grid(row=14, column=0, pady=5, sticky="w")

        # Load saved data
        self.load_saved_data()
        # 添加一个方法来保存数据
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.save_data()
        # 然后销毁窗口
        self.destroy()
    
    def upload_images(self):
        file_path = filedialog.askopenfilename(title="Select Images",filetypes=[("Image", "*.*")])
        if file_path:
            self.cover_path.set(file_path)

    def upload_file(self):
        file_path = filedialog.askopenfilename(title="Select File", filetypes=[("Video Or MD", "*.*")])
        if file_path:
            self.file_path.set(file_path)

    def copy_md_to_clipboard(self):
        md_text = self.file_path.get()
        self.clipboard_clear()
        url=self.md_conv_entry.get()
        file_path = self.file_path.get()
        if url and file_path:
            asyncio.run(md2copy(url=url, file_path=file_path))
        else:
            messagebox.showwarning("Warning", "MD Conversion URL and Fileis not set!")
    def publish_toutiao(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        cover = self.cover_entry.get()
        file_path = self.file_path.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags or not cover or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        asyncio.run(toutiao(title=title, description=description, tags=tags, cover=cover, file_path=file_path))
    def publish_baijiahao(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        cover = self.cover_entry.get()
        file_path = self.file_path.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags or not cover or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        asyncio.run(baijiahao(title=title, description=description, tags=tags, cover=cover, file_path=file_path))

    def publish_zhihu(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        cover = self.cover_entry.get()
        file_path = self.file_path.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags or not cover or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        asyncio.run(zhihu(title=title, description=description, tags=tags, cover=cover, file_path=file_path))

    def publish_wxgzh(self):
        # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        cover = self.cover_entry.get()
        file_path = self.file_path.get()
        author = self.author_entry.get()
        
        # Ensure all fields are filled
        if not title or not description or not tags or not cover or not file_path :
            messagebox.showwarning("Warning", "All fields must be filled!")
            return
        
        asyncio.run(wxgzh(title=title, author=author, description=description, tags=tags, cover=cover, file_path=file_path))

    def save_data(self):
                # Gather data from the UI fields
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        cover = self.cover_entry.get()
        file_path = self.file_path.get()
        md_conv_url = self.md_conv_entry.get()
        author = self.author_entry.get()
        data = {
            "title": title,
            "description": description,
            "tags": tags,
            "cover": cover,  # Save as list
            "file_path": file_path,
            "md_conv_url": md_conv_url,
            "author": author,
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {}

    def load_saved_data(self):
        self.title_entry.insert(0, self.saved_data.get("title", ""))
        self.description_entry.insert(0, self.saved_data.get("description", ""))
        self.tags_entry.insert(0, self.saved_data.get("tags", ""))
        self.cover_path.set(self.saved_data.get("cover", ""))
        self.file_path.set(self.saved_data.get("file_path", ""))
        self.md_conv_entry.insert(0, self.saved_data.get("md_conv_url", ""))
        self.author_entry.insert(0, self.saved_data.get("author", ""))


if __name__ == "__main__":
    # 异步事件循环
    app = ArticlePublisher()
    app.mainloop()