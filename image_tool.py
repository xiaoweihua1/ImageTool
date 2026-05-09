#!/usr/bin/env python3
"""图片压缩工具 - 美化版"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading, os, tempfile, shutil

class App:
    def __init__(self):
        self.root = tb.Window(title="图片压缩工具", themename="darkly")
        self.root.geometry("620x520")
        self.root.minsize(600, 450)
        
        self.images = []
        self.output_dir = None
        
        # 标题
        tb.Label(self.root, text="图片压缩工具", font=("Microsoft YaHei", 20, "bold")).pack(pady=(20,2))
        tb.Label(self.root, text="批量压缩 · 格式转换 · 先预览后压缩", font=("Microsoft YaHei", 9), bootstyle="secondary").pack()
        
        # 操作栏
        action = tb.Frame(self.root)
        action.pack(fill=X, padx=30, pady=8)
        tb.Button(action, text="添加图片", command=self.add, bootstyle="primary", width=12).pack(side=LEFT, padx=3)
        tb.Button(action, text="清空列表", command=self.clear, bootstyle="danger", width=10).pack(side=LEFT, padx=3)
        
        # 图片列表
        list_frame = tb.LabelFrame(self.root, text="已选图片")
        list_frame.pack(fill=BOTH, expand=True, padx=30, pady=5)
        self.tx = tb.Text(list_frame, height=8, font=("Consolas", 9), relief="flat")
        self.tx.pack(fill=BOTH, expand=True, side=LEFT)
        scroll = tb.Scrollbar(list_frame, orient=VERTICAL, command=self.tx.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.tx.configure(yscrollcommand=scroll.set)
        
        # 设置区
        settings = tb.LabelFrame(self.root, text="压缩设置")
        settings.pack(fill=X, padx=30, pady=8)
        
        # 第一行: 格式
        row1 = tb.Frame(settings)
        row1.pack(fill=X, pady=2)
        tb.Label(row1, text="输出格式:", width=10).pack(side=LEFT)
        self.fmt = tb.Combobox(row1, values=["保持原格式","JPEG","PNG","WebP"], state="readonly", width=15)
        self.fmt.current(0)
        self.fmt.pack(side=LEFT, padx=5)
        
        # 第二行: 质量
        row2 = tb.Frame(settings)
        row2.pack(fill=X, pady=2)
        tb.Label(row2, text="压缩质量:", width=10).pack(side=LEFT)
        self.ql = tb.Label(row2, text="80%", width=5)
        self.ql.pack(side=RIGHT)
        self.qs = tk.Scale(row2, from_=1, to=100, orient=tk.HORIZONTAL, length=200,
                          command=lambda v: self.ql.configure(text=f"{int(v)}%"), bg="#2d2d2d", fg="white", troughcolor="#444")
        self.qs.set(80)
        self.qs.pack(side=RIGHT, padx=5)
        
        # 第三行: 输出目录
        row3 = tb.Frame(settings)
        row3.pack(fill=X, pady=2)
        tb.Label(row3, text="输出目录:", width=10).pack(side=LEFT)
        self.op = tb.Label(row3, text="原文件夹（覆盖）", bootstyle="secondary")
        self.op.pack(side=LEFT, padx=5)
        tb.Button(row3, text="选择", command=self.sel_out, bootstyle="secondary", width=8).pack(side=RIGHT)
        
        # 预览按钮
        tb.Button(self.root, text="预览压缩大小", command=self.preview, bootstyle="info", 
                 padding=10).pack(fill=X, padx=30, pady=5)
        
        # 状态
        self.st = tb.Label(self.root, text="就绪", bootstyle="secondary")
        self.st.pack(pady=(0,10))
    
    def add(self):
        fs = filedialog.askopenfilenames(filetypes=[("图片","*.jpg *.jpeg *.png *.gif *.bmp *.webp")])
        for f in fs:
            if f not in [i[0] for i in self.images]:
                self.images.append((f, os.path.basename(f), os.path.getsize(f)/1024))
        self.refresh()
    
    def clear(self):
        self.images.clear()
        self.tx.delete("1.0","end")
        self.tx.insert("end","点击「添加图片」选择要处理的文件")
    
    def refresh(self):
        self.tx.delete("1.0","end")
        t=0
        for _,n,s in self.images:
            self.tx.insert("end",f"  {n}  ({s:.0f}KB)\n"); t+=s
        self.tx.insert("end",f"\n  共 {len(self.images)} 张，总计 {t/1024:.1f}MB")
        self.st.configure(text=f"已选择 {len(self.images)} 张图片")
    
    def sel_out(self):
        d=filedialog.askdirectory()
        if d: self.output_dir=d; self.op.configure(text=d)
    
    def preview(self):
        if not self.images: messagebox.showwarning("提示","请先添加图片"); return
        fm = {"JPEG":"JPEG","PNG":"PNG","WebP":"WebP"}
        tf = fm.get(self.fmt.get())
        q = self.qs.get()
        fr = {"jpg":"JPEG","jpeg":"JPEG","png":"PNG","gif":"GIF","bmp":"BMP","webp":"WebP"}
        se = f".{tf.lower()}" if tf else ".jpg"
        
        tmp = tempfile.mkdtemp()
        self.tx.delete("1.0","end")
        to,tn = 0,0
        
        for p,n,s in self.images:
            to+=s
            try:
                sf = tf or fr.get(os.path.splitext(n)[1].replace(".",""),"JPEG")
                op = os.path.join(tmp,os.path.splitext(n)[0]+se)
                img = Image.open(p)
                if img.mode in ('RGBA','P') and sf=="JPEG": img=img.convert("RGB")
                img.save(op,sf,quality=q,optimize=True) if sf=="JPEG" else img.save(op,sf,optimize=True)
                nk = os.path.getsize(op)/1024; tn+=nk
                ra = (s-nk)/s*100
                self.tx.insert("end",f"  {n}\n    原{s:.0f}KB → {nk:.0f}KB (省{ra:.0f}%) \n")
            except:
                self.tx.insert("end",f"  {n}  处理失败\n")
            self.st.configure(text=f"估算中...")
        
        shutil.rmtree(tmp,ignore_errors=True)
        sp = (to-tn)/to*100 if to else 0
        self.tx.insert("end",f"\n  合计: 原 {to/1024:.1f}MB → {tn/1024:.1f}MB (省{sp:.0f}%)")
        self.st.configure(text="预览完成，可点击执行压缩")
        
        if messagebox.askyesno("确认压缩",f"原大小: {to/1024:.1f}MB\n压缩后: {tn/1024:.1f}MB\n节省: {(to-tn)/1024:.1f}MB\n\n是否执行压缩？"):
            self.do_compress(tf,q,fr,se)
    
    def do_compress(self,tf,q,fr,se):
        def go():
            suc,fal=0,0
            for p,n,_ in self.images:
                try:
                    sf = tf or fr.get(os.path.splitext(n)[1].replace(".",""),"JPEG")
                    op = os.path.join(self.output_dir or os.path.dirname(p),os.path.splitext(n)[0]+se)
                    img = Image.open(p)
                    if img.mode in ('RGBA','P') and sf=="JPEG": img=img.convert("RGB")
                    os.makedirs(os.path.dirname(op),exist_ok=True)
                    img.save(op,sf,quality=q,optimize=True) if sf=="JPEG" else img.save(op,sf,optimize=True)
                    suc+=1
                except: fal+=1
            self.root.after(0,lambda: (self.st.configure(text=f"完成！成功{suc}张，失败{fal}张"),
                                       messagebox.showinfo("完成",f"成功{suc}张\n失败{fal}张")))
        threading.Thread(target=go,daemon=True).start()
        self.st.configure(text="正在压缩...")

if __name__=="__main__":
    App().root.mainloop()
