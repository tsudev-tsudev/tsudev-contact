# -*- coding: utf-8 -*-
"""Cửa sổ xem trước danh bạ đã nạp, có phân trang."""
import tkinter as tk
from tkinter import ttk

from src.services.tokens import DEFAULT_THEME, loadTokens

PAGE_SIZE = 50
WINDOW_SIZE = "900x600"
COLUMN_WIDTH = 120


class PreviewWindow(tk.Toplevel):
    def __init__(self, parent, db, columnsMap, totalItems, iconPhoto, theme=DEFAULT_THEME):
        super().__init__(parent)
        self.db, self.columnsMap, self.totalItems = db, columnsMap, totalItems
        self.tokens = loadTokens(theme)
        self.configure(bg=self.tokens.color('bg-base'))
        self.pageSize, self.currentPage = PAGE_SIZE, 1
        self.totalPages = max(1, (totalItems + self.pageSize - 1) // self.pageSize)

        self.title("Xem trước Toàn bộ Danh bạ")
        self.geometry(WINDOW_SIZE)
        if iconPhoto:
            try:
                self.iconphoto(True, iconPhoto)
            except tk.TclError:
                pass
        self.transient(parent)
        self.grab_set()

        mainFrame = ttk.Frame(self, padding=self.tokens.space(3))
        mainFrame.pack(fill=tk.BOTH, expand=True)
        mainFrame.rowconfigure(0, weight=1)
        mainFrame.columnconfigure(0, weight=1)
        self._createTreeview(mainFrame)
        self._createPaginationControls(mainFrame)
        self.loadPage()

    def _createTreeview(self, parent):
        treeFrame = ttk.Frame(parent)
        treeFrame.grid(row=0, column=0, sticky='nsew')
        self.columnsDef = {key: name.replace('*', '') for key, name in self.columnsMap.items()}
        self.tree = ttk.Treeview(treeFrame, columns=list(self.columnsDef.keys()), show="headings")
        for key, name in self.columnsDef.items():
            self.tree.heading(key, text=name)
            self.tree.column(key, width=COLUMN_WIDTH, anchor='w')

        vsb = ttk.Scrollbar(treeFrame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(treeFrame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.tag_configure('failed_row',
                                background=self.tokens.color('danger'),
                                foreground=self.tokens.color('on-status'))

    def _createPaginationControls(self, parent):
        gap = self.tokens.space(1)
        controlsFrame = ttk.Frame(parent, padding=(0, self.tokens.space(3), 0, 0))
        controlsFrame.grid(row=1, column=0, sticky='ew')
        controlsFrame.columnconfigure(2, weight=1)

        self.firstBtn = ttk.Button(controlsFrame, text="<< Đầu", command=lambda: self.goToPage(1))
        self.firstBtn.grid(row=0, column=0, padx=gap)
        self.prevBtn = ttk.Button(controlsFrame, text="< Trước", command=self.prevPage)
        self.prevBtn.grid(row=0, column=1, padx=gap)
        self.pageLabelVar = tk.StringVar()
        ttk.Label(controlsFrame, textvariable=self.pageLabelVar,
                  font=self.tokens.font('body-desktop')).grid(row=0, column=2)
        self.nextBtn = ttk.Button(controlsFrame, text="Sau >", command=self.nextPage)
        self.nextBtn.grid(row=0, column=3, padx=gap)
        self.lastBtn = ttk.Button(controlsFrame, text="Cuối >>",
                                  command=lambda: self.goToPage(self.totalPages))
        self.lastBtn.grid(row=0, column=4, padx=gap)

    def loadPage(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for contact in self.db.getContactsPaginated(self.currentPage, self.pageSize):
            # sqlite3.Row không có .get() — truy cập bằng khóa, cột luôn tồn tại trong schema
            values = [contact[key] or '' for key in self.columnsDef]
            tags = ('failed_row',) if contact['status'] == 'failed' else ()
            self.tree.insert("", tk.END, values=values, tags=tags)
        self.updateControls()

    def updateControls(self):
        self.pageLabelVar.set(
            f"Trang {self.currentPage} / {self.totalPages} (Tổng: {self.totalItems} mục)")
        state = 'normal' if self.currentPage > 1 else 'disabled'
        self.firstBtn['state'] = self.prevBtn['state'] = state
        state = 'normal' if self.currentPage < self.totalPages else 'disabled'
        self.nextBtn['state'] = self.lastBtn['state'] = state

    def goToPage(self, pageNum):
        self.currentPage = pageNum
        self.loadPage()

    def nextPage(self):
        if self.currentPage < self.totalPages:
            self.goToPage(self.currentPage + 1)

    def prevPage(self):
        if self.currentPage > 1:
            self.goToPage(self.currentPage - 1)
