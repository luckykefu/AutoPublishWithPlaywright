import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
import json
import os

DATA_FILE = "saved_data.json"

class ArticlePublisher(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        
        self.title("Article Publisher")
        self.geometry("800x600")

        self.saved_data = self.load_data()

        # Left column
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

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

        # Cover Image
        self.cover_label = ttk.Label(left_frame, text="Cover Image")
        self.cover_label.grid(row=3, column=0, pady=5, sticky="e")
        self.cover_button = ttk.Button(left_frame, text="Upload Image", command=self.upload_image, bootstyle="primary")
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

        # Right column
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.platform_label = ttk.Label(right_frame, text="Publish Platforms")
        self.platform_label.grid(row=0, column=0, pady=5)

        self.weixin_button = ttk.Button(right_frame, text="Publish to WeChat", command=lambda: self.publish_article("WeChat"), bootstyle="success")
        self.weixin_button.grid(row=1, column=0, pady=5, sticky="w")

        self.zhihu_button = ttk.Button(right_frame, text="Publish to Zhihu", command=lambda: self.publish_article("Zhihu"), bootstyle="success")
        self.zhihu_button.grid(row=2, column=0, pady=5, sticky="w")

        self.weibo_button = ttk.Button(right_frame, text="Publish to Weibo", command=lambda: self.publish_article("Weibo"), bootstyle="success")
        self.weibo_button.grid(row=3, column=0, pady=5, sticky="w")

        self.qq_button = ttk.Button(right_frame, text="Publish to QQ Space", command=lambda: self.publish_article("QQ Space"), bootstyle="success")
        self.qq_button.grid(row=4, column=0, pady=5, sticky="w")

        # Output text box
        self.output_text = tk.Text(self, height=10, width=90, state='disabled')
        self.output_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Load saved data
        self.load_saved_data()

    def upload_image(self):
        file_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.cover_path.set(file_path)

    def upload_file(self):
        file_path = filedialog.askopenfilename(title="Select File", filetypes=[("All Files", "*.*")])
        if file_path:
            self.file_path.set(file_path)

    def publish_article(self, platform):
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = self.tags_entry.get()
        cover = self.cover_path.get()
        file_url = self.file_path.get()

        if not title or not description or not tags or not cover or not file_url:
            messagebox.showwarning("Warning", "All fields must be filled!")
            return

        # Simulate publishing operation
        output = f"Publishing Article to {platform}:\nTitle: {title}\nDescription: {description}\nTags: {tags}\nCover Image: {cover}\nFile URL: {file_url}\n"
        self.display_output(output)
        
        messagebox.showinfo("Success", f"Article published to {platform} successfully!")
        
        # Save data to file
        self.save_data({
            "title": title,
            "description": description,
            "tags": tags,
            "cover": cover,
            "file_url": file_url
        })

        # Clear the entries
        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.tags_entry.delete(0, tk.END)
        self.cover_path.set('')
        self.file_path.set('')

    def save_data(self, data):
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)

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
        self.file_path.set(self.saved_data.get("file_url", ""))

    def display_output(self, output):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, output + "\n")
        self.output_text.config(state='disabled')

if __name__ == "__main__":
    app = ArticlePublisher()
    app.mainloop()