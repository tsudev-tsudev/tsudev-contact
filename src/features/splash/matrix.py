# -*- coding: utf-8 -*-
"""Cửa sổ hiệu ứng "mưa ký tự" hiển thị trước khi vào ứng dụng chính."""
import random
import time
import tkinter as tk

from src.services.tokens import loadTokens

WINDOW_WIDTH, WINDOW_HEIGHT = 500, 300
DURATION_SECONDS = 3
FRAME_DELAY_MS = 30
GLYPHS = '0123456789ABCDEF'


class MatrixWindow(tk.Toplevel):
    def __init__(self, parent, onComplete):
        super().__init__(parent)
        self.onComplete = onComplete
        self.tokens = loadTokens('dark')  # màn hình hiệu ứng luôn dùng chủ đề tối
        self.glyphColor = self.tokens.color('success')

        self.overrideredirect(True)
        self.configure(bg=self.tokens.color('bg-base'))
        x = (self.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        self.attributes("-topmost", True)

        self.canvas = tk.Canvas(self, bg=self.tokens.color('bg-base'), highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.font = self.tokens.font('xs', mono=True)
        columnStep = self.tokens.size('xs')
        self.columns = [
            {'x': x, 'y': -random.randint(50, WINDOW_HEIGHT), 'speed': random.uniform(2, 5)}
            for x in range(0, WINDOW_WIDTH, columnStep)
        ]
        self.startTime = time.time()
        self.updateAnimation()

    def updateAnimation(self):
        self.canvas.delete('all')
        for col in self.columns:
            self.canvas.create_text(col['x'], col['y'], text=random.choice(GLYPHS),
                                    fill=self.glyphColor, font=self.font)
            col['y'] += col['speed']
            if col['y'] > self.winfo_height():
                col['y'] = -random.randint(20, 50)
        if time.time() - self.startTime > DURATION_SECONDS:
            self.finish()
        else:
            self.after(FRAME_DELAY_MS, self.updateAnimation)

    def finish(self):
        self.destroy()
        self.onComplete()
