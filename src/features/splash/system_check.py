# -*- coding: utf-8 -*-
"""Cửa sổ hiệu ứng "kiểm tra hệ thống" hiển thị trước khi vào ứng dụng chính."""
import random
import time
import tkinter as tk
from tkinter import ttk, scrolledtext

from src.services.tokens import loadTokens

WINDOW_WIDTH, WINDOW_HEIGHT = 400, 200
DURATION_SECONDS = 2.5
FRAME_DELAY_MS = 50
FINISH_DELAY_MS = 500
CHARS_PER_LINE = 50


class SystemCheckWindow(tk.Toplevel):
    def __init__(self, parent, onComplete):
        super().__init__(parent)
        self.onComplete = onComplete
        self.tokens = loadTokens('dark')  # màn hình hiệu ứng luôn dùng chủ đề tối
        bg = self.tokens.color('bg-base')
        accent = self.tokens.color('success')

        self.overrideredirect(True)
        self.configure(bg=bg)
        x = (self.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        self.attributes("-topmost", True)

        self.scanText = scrolledtext.ScrolledText(
            self, bg=bg, fg=accent, font=self.tokens.font('xs', mono=True),
            wrap=tk.WORD, insertbackground=accent)
        self.scanText.pack(expand=True, fill=tk.BOTH,
                           padx=self.tokens.space(3), pady=self.tokens.space(1))
        self.scanText.config(state='disabled')

        self.progress = ttk.Progressbar(self, length=WINDOW_WIDTH - self.tokens.space(5),
                                        mode='determinate')
        self.progress.pack(pady=self.tokens.space(3))

        self.statusLabel = ttk.Label(
            self, text="KHỞI TẠO HỆ THỐNG...", background=bg, foreground=accent,
            font=self.tokens.font('sm', 'bold', mono=True))
        self.statusLabel.pack(pady=self.tokens.space(1))

        self.startTime = time.time()
        self.updateAnimation()

    def updateAnimation(self):
        self.scanText.config(state='normal')
        self.scanText.insert(tk.END, ''.join(random.choice('01') for _ in range(CHARS_PER_LINE)) + '\n')
        self.scanText.see(tk.END)
        self.scanText.config(state='disabled')

        elapsed = time.time() - self.startTime
        self.progress['value'] = min((elapsed / DURATION_SECONDS) * 100, 100)
        if elapsed >= DURATION_SECONDS:
            self.statusLabel.config(text="KHỞI TẠO THÀNH CÔNG!")
            self.after(FINISH_DELAY_MS, self.finish)
        else:
            self.after(FRAME_DELAY_MS, self.updateAnimation)

    def finish(self):
        self.destroy()
        self.onComplete()
