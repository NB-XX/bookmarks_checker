import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
from bs4 import BeautifulSoup
import requests
import threading

class BookmarkApp:
    def __init__(self, root):
        self.root = root
        root.title("书签检查器")
        self.proxy = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}  
        self.timeout = 10  
        self.output_directory = ""       

        # Configuration Frame
        self.config_frame = tk.Frame(root, height=50, bg='lightgrey')
        self.config_frame.pack(fill=tk.X, padx=10, pady=5)
        self.config_label = tk.Label(self.config_frame, text="代理配置：", bg='lightgrey')
        self.config_label.pack(side=tk.LEFT, padx=5)
        self.proxy_entry = tk.Entry(self.config_frame, width=30)
        self.proxy_entry.pack(side=tk.LEFT, padx=5)
        self.proxy_entry.insert(0, "127.0.0.1:7890")  
        self.timeout_label = tk.Label(self.config_frame, text="超时时间", bg='lightgrey')
        self.timeout_label.pack(side=tk.LEFT, padx=5)
        self.timeout_entry = tk.Entry(self.config_frame, width=5)
        self.timeout_entry.pack(side=tk.LEFT, padx=5)
        self.timeout_entry.insert(0, "10")
        self.output_button = tk.Button(self.config_frame, text="输出文件夹", command=self.choose_output_directory)
        self.output_button.pack(side=tk.LEFT, padx=5)
        self.confirm_button = tk.Button(self.config_frame, text="确认修改", command=self.update_config)
        self.confirm_button.pack(side=tk.LEFT, padx=5)

        # Input Frame for drag and drop
        self.input_frame = tk.Frame(root, height=100, bg='lightgrey')
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        self.input_label = tk.Label(self.input_frame, text="点击添加书签文件", bg='lightgrey')
        self.input_label.pack(pady=30)
        
        # Output Frame for results
        self.output_frame = tk.Frame(root, bg='white')
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.output_label = tk.Label(self.output_frame, text="处理结果：", bg='white')
        self.output_label.pack(pady=5)
        self.output_list = tk.Listbox(self.output_frame, bg='white')
        self.output_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.scrollbar = tk.Scrollbar(self.output_frame, command=self.output_list.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_list.config(yscrollcommand=self.scrollbar.set)

        # Bind events
        self.input_frame.bind("<Button-1>", self.load_file)
        self.output_list.bind("<Double-1>", self.open_link)

    def load_file(self, event):
        filepath = filedialog.askopenfilename()
        if filepath:
            threading.Thread(target=self.process_bookmarks, args=(filepath,)).start()

    def process_bookmarks(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

            links = soup.find_all('a')
            for link in links:
                self.root.after(0, self.output_list.insert, tk.END, f"⏳ 正在检查: {link.text or '无标题'}")
                is_good = self.check_url(link)
                self.root.after(0, self.update_listbox, link, is_good)
            
        except Exception as e:
            messagebox.showerror("错误", f"处理文件失败: {e}")

    def check_url(self, link):
        url = link.get('href')
        try:
            response = requests.get(url, timeout=10)
            return response.status_code != 404
        except Exception as e:
            return False

    def update_listbox(self, link, is_good):
        for i in range(self.output_list.size()):
            if self.output_list.get(i).endswith(link.text or '无标题'):
                symbol = "✅" if is_good else "❌"
                self.output_list.delete(i)
                self.output_list.insert(i, f"{symbol} {link.text or '无标题'} ({link.get('href')})")
                break

    def open_link(self, event):
        selection = self.output_list.curselection()
        if selection:
            url = self.output_list.get(selection[0])
            url = url.split(" ")[-1]  # Assumes URL is the last part
            url = url.replace('(', '').replace(')', '').strip()
            webbrowser.open(url)



    def choose_output_directory(self):
        chosen_directory = filedialog.askdirectory()
        if chosen_directory:
            self.output_directory = chosen_directory
            messagebox.showinfo("文件夹选择", "选择输出文件夹成功")
        else:
            self.output_directory = "" 
            messagebox.showinfo("文件夹选择", "未选择新的文件夹，将使用默认程序启动目录")

    def update_config(self):
        try:
            if self.proxy_entry.get():
                self.proxy = {"http": self.proxy_entry.get(), "https": self.proxy_entry.get()}
            if self.timeout_entry.get():
                self.timeout = int(self.timeout_entry.get())
            messagebox.showinfo("配置更新", "配置更改成功")
        except ValueError as e:
            messagebox.showerror("错误", "请检查是否输入了正确的代理地址和超时时间")

# Run the application
root = tk.Tk()
app = BookmarkApp(root)
root.mainloop()