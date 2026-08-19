# -*- coding: utf-8 -*-
# --- Tác giả: nguyentrangtinhsu ---
# --- Phiên bản: 5.2 (Robust Edition) ---

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
import csv
import os
import sys
import threading
import webbrowser
from datetime import datetime
import ctypes
from PIL import Image, ImageTk
import sqlite3
import random
import time

# --- Cấu hình cho màn hình HiDPI trên Windows ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# --- Hàm tìm đường dẫn tài nguyên khi đã đóng gói bằng PyInstaller ---
def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cho cả dev và PyInstaller. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Lớp quản lý Cơ sở dữ liệu ---
class DatabaseManager:
    """ Quản lý cơ sở dữ liệu SQLite để lưu trữ danh bạ. """
    def __init__(self, db_file='contacts_data.db'):
        self.db_file = resource_path(db_file)
        self._setup_database()

    def _get_conn(self):
        return sqlite3.connect(self.db_file)

    def _setup_database(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL, number TEXT NOT NULL, email TEXT,
                    organization TEXT, address TEXT, birthday TEXT, notes TEXT,
                    status TEXT DEFAULT 'success', original_row INTEGER
                )
            ''')
            conn.commit()

    def clear_all_contacts(self):
        with self._get_conn() as conn:
            conn.cursor().execute("DELETE FROM contacts")
            conn.commit()

    def add_contact(self, data: dict):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO contacts (name, number, email, organization, address, birthday, notes, status, original_row)
                VALUES (:name, :number, :email, :organization, :address, :birthday, :notes, :status, :original_row)
            ''', data)
            conn.commit()

    def get_contact_count(self) -> int:
        with self._get_conn() as conn:
            return conn.cursor().execute("SELECT COUNT(id) FROM contacts").fetchone()[0]

    def get_contacts_paginated(self, page: int, page_size: int) -> list:
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            offset = (page - 1) * page_size
            cursor.execute("SELECT * FROM contacts ORDER BY original_row LIMIT ? OFFSET ?", (page_size, offset))
            return cursor.fetchall()

# --- Các lớp Giao diện Hiệu ứng ---
class SystemCheckWindow(tk.Toplevel):
    """ Cửa sổ hiệu ứng kiểm tra hệ thống. """
    def __init__(self, parent, on_complete):
        super().__init__(parent)
        self.on_complete = on_complete
        self.overrideredirect(True); self.configure(bg='black')
        width, height = 400, 200
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}"); self.attributes("-topmost", True)
        self.scan_text = scrolledtext.ScrolledText(self, bg='black', fg='#00ff41', font=('Consolas', 9), wrap=tk.WORD, insertbackground='#00ff41')
        self.scan_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=5); self.scan_text.config(state='disabled')
        self.progress = ttk.Progressbar(self, length=380, mode='determinate'); self.progress.pack(pady=10)
        self.status_label = ttk.Label(self, text="KHỞI TẠO HỆ THỐNG...", background='black', foreground='#00ff41', font=('Consolas', 10, 'bold'))
        self.status_label.pack(pady=5)
        self.start_time = time.time(); self.duration = 2.5
        self.update_animation()

    def update_animation(self):
        self.scan_text.config(state='normal')
        self.scan_text.insert(tk.END, ''.join(random.choice('01') for _ in range(50)) + '\n'); self.scan_text.see(tk.END)
        self.scan_text.config(state='disabled')
        elapsed = time.time() - self.start_time
        self.progress['value'] = min((elapsed / self.duration) * 100, 100)
        if elapsed >= self.duration:
            self.status_label.config(text="KHỞI TẠO THÀNH CÔNG!")
            self.after(500, self.finish)
        else:
            self.after(50, self.update_animation)

    def finish(self):
        self.destroy(); self.on_complete()

class MatrixWindow(tk.Toplevel):
    def __init__(self, parent, on_complete):
        super().__init__(parent)
        self.on_complete = on_complete
        self.overrideredirect(True); self.configure(bg='black')
        width, height = 500, 300
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}"); self.attributes("-topmost", True)
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0); self.canvas.pack(fill=tk.BOTH, expand=True)
        font_size = 12; self.font = ('Consolas', font_size)
        self.columns = [{'x': x, 'y': -random.randint(50, height), 'speed': random.uniform(2, 5)} for x in range(0, width, font_size)]
        self.start_time = time.time(); self.duration = 3
        self.update_animation()

    def update_animation(self):
        self.canvas.delete('all')
        for col in self.columns:
            self.canvas.create_text(col['x'], col['y'], text=random.choice('0123456789ABCDEF'), fill='#00ff41', font=self.font)
            col['y'] += col['speed']
            if col['y'] > self.winfo_height(): col['y'] = -random.randint(20, 50)
        if time.time() - self.start_time > self.duration: self.finish()
        else: self.after(30, self.update_animation)

    def finish(self):
        self.destroy(); self.on_complete()

# --- Lớp Ứng dụng chính ---
class ContactsApp:
    def __init__(self, root, icon_photo):
        self.root = root; self.icon_photo = icon_photo
        self.db = DatabaseManager(); self.last_saved_folder = None; self.preview_columns = []
        self.root.title("Contacts - Chuyển đổi CSV sang vCard (v5.2)")
        if self.icon_photo:
            try: self.root.iconphoto(True, self.icon_photo)
            except tk.TclError: pass
        self._configure_styles(); self._create_menu(); self._create_widgets()

    def _configure_styles(self):
        self.style = ttk.Style(self.root); self.style.theme_use('vista')
        bg_color = '#f0f0f0'
        self.style.configure('TLabel', font=('Segoe UI', 10), background=bg_color)
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=6)
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabelframe', padding=10, background=bg_color)
        self.style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'), foreground='#003d7a', background=bg_color)
        self.style.configure('Link.TLabel', font=('Segoe UI', 9, 'underline'), foreground='blue', background=bg_color)
        self.style.configure('Watermark.TLabel', font=('Segoe UI', 9, 'italic'), foreground='#a0a0a0', background=bg_color)
        self.style.configure('Progress.TLabel', font=('Segoe UI', 9, 'bold'), background='transparent')
        self.style.configure('Success.Horizontal.TProgressbar', background='#28a745')
        self.style.configure('Required.TLabel', font=('Segoe UI', 10, 'bold'), foreground='red', background=bg_color)
        self.style.configure('Highlight.TButton', font=('Segoe UI', 10, 'bold'), foreground='white', background='#0078d7')
        self.style.map('Highlight.TButton', background=[('active', '#005a9e')])

    def _create_menu(self):
        menu_bar = tk.Menu(self.root); self.root.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Tệp", menu=file_menu)
        file_menu.add_command(label="Chọn file CSV...", command=self._browse_csv, accelerator="Ctrl+O")
        file_menu.add_command(label="Chọn nơi lưu VCF...", command=self._browse_vcf, accelerator="Ctrl+S")
        file_menu.add_separator(); file_menu.add_command(label="Thoát", command=self.root.quit)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Trợ giúp", menu=help_menu)
        help_menu.add_command(label="Về ứng dụng", command=self._show_about_dialog, accelerator="F1")
        self.root.bind("<Control-o>", lambda e: self._browse_csv())
        self.root.bind("<Control-s>", lambda e: self._browse_vcf())
        self.root.bind("<F1>", lambda e: self._show_about_dialog())

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        file_frame = ttk.LabelFrame(main_frame, text="Bước 1: Chọn File Nguồn và Đích")
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10)); file_frame.columnconfigure(1, weight=1)
        ttk.Label(file_frame, text="File CSV:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.csv_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.csv_path_var, state='readonly').grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(file_frame, text="Chọn...", command=self._browse_csv).grid(row=0, column=2, padx=5)
        ttk.Label(file_frame, text="Lưu VCF:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.vcf_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.vcf_path_var, state='readonly').grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(file_frame, text="Lưu tại...", command=self._browse_vcf).grid(row=1, column=2, padx=5)
        self.mapping_frame = ttk.LabelFrame(main_frame, text="Bước 2: Ghép Nối Dữ Liệu")
        self.mapping_frame.grid(row=1, column=0, sticky="ew", pady=10); self.mapping_frame.columnconfigure((0, 1, 2), weight=1)
        self.field_mappings = {}; self._create_field_mapping_widgets()
        action_frame = ttk.Frame(main_frame); action_frame.grid(row=2, column=0, pady=15)
        self.convert_button = ttk.Button(action_frame, text="BẮT ĐẦU CHUYỂN ĐỔI", command=self._start_conversion, style='Highlight.TButton', padding=10)
        self.convert_button.pack()
        self.status_text = tk.StringVar(value="Chưa chọn file CSV")
        ttk.Label(main_frame, textvariable=self.status_text, font=('Segoe UI', 9), foreground='#555').grid(row=3, column=0, sticky="ew", pady=(0, 5))
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate"); self.progress.grid(row=4, column=0, sticky="ew")
        log_container = ttk.LabelFrame(main_frame, text="Nhật Ký Chuyển Đổi")
        log_container.grid(row=5, column=0, sticky="nsew", pady=(10, 0)); log_container.columnconfigure(0, weight=1); log_container.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        self.status_log = scrolledtext.ScrolledText(log_container, height=5, font=('Consolas', 9), wrap=tk.WORD, relief=tk.SOLID, borderwidth=1, state="disabled")
        self.status_log.grid(row=0, column=0, sticky="nsew")
        bottom_frame = ttk.Frame(main_frame); bottom_frame.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        self.open_folder_button = ttk.Button(bottom_frame, text="Mở thư mục", command=self._open_saved_folder, state="disabled"); self.open_folder_button.pack(side=tk.LEFT)
        self.preview_button = ttk.Button(bottom_frame, text="Xem thử Danh bạ", command=self._show_preview_dialog, state="disabled"); self.preview_button.pack(side=tk.LEFT, padx=5)
        author_frame = ttk.Frame(bottom_frame); author_frame.pack(side=tk.RIGHT)
        ttk.Label(author_frame, text="nguyentrangtinhsu", style='Watermark.TLabel').pack(anchor='e')
        support_label = ttk.Label(author_frame, text="Hỗ trợ qua Facebook", style='Link.TLabel', cursor="hand2"); support_label.pack(anchor='e')
        support_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.facebook.com/nguyentrangtinhsu"))

    def _create_field_mapping_widgets(self, headers=[]):
        for widget in self.mapping_frame.winfo_children(): widget.destroy()
        vcard_fields = {'name': 'Tên*', 'number': 'SĐT*', 'email': 'Email', 'organization': 'Tổ chức', 'address': 'Địa chỉ', 'notes': 'Ghi chú', 'birthday': 'Ngày sinh'}
        options = ['(Bỏ qua)'] + headers
        for i, (field, label_text) in enumerate(vcard_fields.items()):
            row, col = divmod(i, 3)
            field_frame = ttk.Frame(self.mapping_frame); field_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            if '*' in label_text:
                label_container = ttk.Frame(field_frame); label_container.pack(side=tk.LEFT, padx=(0,5))
                ttk.Label(label_container, text=label_text.replace('*', '')).pack(side=tk.LEFT)
                ttk.Label(label_container, text='*', style='Required.TLabel').pack(side=tk.LEFT)
            else:
                ttk.Label(field_frame, text=label_text).pack(side=tk.LEFT, padx=(0,5))
            combo = ttk.Combobox(field_frame, values=options, state='readonly', width=15); combo.pack(side=tk.LEFT, expand=True, fill=tk.X)
            combo.set(next((h for h in headers if field in h.lower().replace(' ', '').replace('_', '')), options[0]))
            self.field_mappings[field] = combo

    def _browse_csv(self):
        filepath = filedialog.askopenfilename(title="Chọn file danh bạ CSV", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filepath:
            self.csv_path_var.set(filepath); self.vcf_path_var.set(os.path.splitext(filepath)[0] + '.vcf')
            self._log_message(f"Đã chọn file CSV: {os.path.basename(filepath)}")
            self.status_text.set("Sẵn sàng, vui lòng ghép nối dữ liệu và bắt đầu.")
            self._load_csv_headers()

    def _browse_vcf(self):
        filepath = filedialog.asksaveasfilename(title="Lưu file vCard", defaultextension=".vcf", filetypes=[("vCard files", "*.vcf"), ("All files", "*.*")])
        if filepath: self.vcf_path_var.set(filepath); self._log_message(f"Sẽ lưu file VCF tại: {os.path.basename(filepath)}")

    def _load_csv_headers(self):
        try:
            with open(self.csv_path_var.get(), mode='r', encoding='utf-8-sig', newline='') as f:
                self._create_field_mapping_widgets(next(csv.reader(f)))
                self._log_message("Đã đọc các cột từ CSV. Vui lòng kiểm tra và ghép nối.")
        except Exception as e:
            messagebox.showerror("Lỗi đọc file", f"Không thể đọc header từ file CSV:\n{e}", parent=self.root)
            self._log_message(f"Lỗi đọc file CSV: {e}", "error")

    def _start_conversion(self):
        if not self.csv_path_var.get() or not self.vcf_path_var.get():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn file CSV nguồn và nơi lưu VCF.", parent=self.root); return
        if self.field_mappings['name'].get() == '(Bỏ qua)' or self.field_mappings['number'].get() == '(Bỏ qua)':
            messagebox.showwarning("Thiếu thông tin", "Bạn phải chọn cột cho 'Tên' và 'SĐT'.", parent=self.root); return
        self.convert_button.config(state="disabled")
        for btn in [self.preview_button, self.open_folder_button]: btn.config(state="disabled")
        self.preview_columns = {field: combo.get() for field, combo in self.field_mappings.items() if combo.get() != '(Bỏ qua)'}
        mappings = {field: combo.get() for field, combo in self.field_mappings.items()}
        threading.Thread(target=self._conversion_logic, args=(self.csv_path_var.get(), self.vcf_path_var.get(), mappings), daemon=True).start()

    def _conversion_logic(self, csv_path, vcf_path, mappings):
        try:
            self.db.clear_all_contacts()
            with open(csv_path, 'r', encoding='utf-8-sig', errors='ignore') as f: total_rows = sum(1 for r in f if r.strip()) - 1
            if total_rows <= 0: raise ValueError("File CSV rỗng hoặc chỉ có tiêu đề.")
            
            with open(csv_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                reader = csv.DictReader(f)
                all_db_fields = ['name', 'number', 'email', 'organization', 'address', 'birthday', 'notes']
                
                for i, row in enumerate(reader):
                    data = {'original_row': i + 2}
                    for field, csv_header in mappings.items():
                        if csv_header != '(Bỏ qua)':
                            data[field] = row.get(csv_header, '')
                    
                    for field in all_db_fields:
                        if field not in data:
                            data[field] = ''
                    
                    # *** SỬA LỖI 'NoneType' TẠI ĐÂY ***
                    # Luôn đảm bảo giá trị là chuỗi trước khi gọi .strip()
                    name_val = data.get('name') or ''
                    number_val = data.get('number') or ''
                    data['status'] = 'success' if name_val.strip() and number_val.strip() else 'failed'

                    if data['status'] == 'failed': self.root.after(0, self._log_message, f"Lỗi dòng {i+2}: Thiếu Tên/SĐT.", "error")
                    
                    self.db.add_contact(data)
                    self.root.after(0, self._update_progress, (i + 1) / total_rows * 80, f"Đang nhập dòng {i+2}/{total_rows+1}...")

            contacts = self.db.get_contacts_paginated(1, self.db.get_contact_count())
            successful_contacts = [c for c in contacts if c['status'] == 'success']; total_success = len(successful_contacts)
            vcf_content = ""
            for i, contact in enumerate(successful_contacts):
                parts = ["BEGIN:VCARD", "VERSION:3.0", f"FN;CHARSET=UTF-8:{contact['name']}", f"TEL;TYPE=CELL:{contact['number']}"]
                if email := (contact.get('email') or ''): parts.append(f"EMAIL:{email}")
                if org := (contact.get('organization') or ''): parts.append(f"ORG;CHARSET=UTF-8:{org}")
                if addr := (contact.get('address') or ''): parts.append(f"ADR;TYPE=HOME;CHARSET=UTF-8:;;{addr};;;;")
                if bday := (contact.get('birthday') or ''): parts.append(f"BDAY:{bday}")
                if notes := (contact.get('notes') or ''): parts.append(f"NOTE;CHARSET=UTF-8:{notes.replace('\n', '\\n')}")
                parts.append(f"REV:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}"); parts.append("END:VCARD")
                vcf_content += "\n".join(parts) + "\n\n"
                self.root.after(0, self._update_progress, 80 + ((i + 1) / total_success * 20) if total_success > 0 else 100, f"Đang xuất liên hệ {i+1}/{total_success}...")
            
            with open(vcf_path, 'w', encoding='utf-8') as f: f.write(vcf_content)
            self._log_message("--- HOÀN THÀNH ---", "success"); self._log_message(f"Đã xuất thành công: {total_success} liên hệ.", "success")
            if skipped := total_rows - total_success: self._log_message(f"Đã bỏ qua do lỗi: {skipped} dòng.")
            self.root.after(0, self._update_progress, 100, f"Hoàn tất! Đã lưu {total_success} liên hệ.", "success")
            self.last_saved_folder = os.path.dirname(vcf_path)
            for btn in [self.preview_button, self.open_folder_button]: btn.config(state="normal")
            messagebox.showinfo("Thành công", f"Đã xử lý và lưu thành công {total_success} liên hệ.", parent=self.root)
        except Exception as e:
            self._log_message(f"Lỗi nghiêm trọng: {e}", "error"); self.root.after(0, self._update_progress, 0, "Chuyển đổi thất bại!", "error")
            messagebox.showerror("Đã xảy ra lỗi", f"Một lỗi đã xảy ra:\n{e}", parent=self.root)
        finally:
            self.convert_button.config(state="normal")

    def _update_progress(self, value, text):
        self.progress['value'] = value; self.status_text.set(f"{text} ({value:.0f}%)")
        self.progress.config(style='Success.Horizontal.TProgressbar' if value >= 100 else 'Horizontal.TProgressbar')
        if value >= 100: self.status_text.set(text)

    def _log_message(self, message, level="normal"):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.status_log.config(state=tk.NORMAL)
        self.status_log.insert(tk.END, f"[{timestamp}] {message}\n")
        if level in ["success", "error"]: self.status_log.tag_add(level, f"end-{len(message)+2}c", "end-1c")
        self.status_log.tag_configure("success", foreground="green")
        self.status_log.tag_configure("error", foreground="red", font=('Consolas', 9, 'bold'))
        self.status_log.see(tk.END); self.status_log.config(state=tk.DISABLED)

    def _open_saved_folder(self):
        if self.last_saved_folder: webbrowser.open(os.path.realpath(self.last_saved_folder))

    def _show_about_dialog(self):
        messagebox.showinfo("Về ứng dụng", "Contacts - Chuyển đổi CSV sang vCard\nPhiên bản: 5.2\n\nTác giả: nguyentrangtinhsu", parent=self.root)

    def _show_preview_dialog(self):
        total_contacts = self.db.get_contact_count()
        if not total_contacts: messagebox.showinfo("CSDL Rỗng", "Chưa có dữ liệu.", parent=self.root); return
        PreviewWindow(self.root, self.db, self.preview_columns, total_contacts, self.icon_photo)

class PreviewWindow(tk.Toplevel):
    def __init__(self, parent, db, columns_map, total_items, icon_photo):
        super().__init__(parent)
        self.db, self.columns_map, self.total_items = db, columns_map, total_items
        self.page_size, self.current_page = 50, 1
        self.total_pages = (total_items + self.page_size - 1) // self.page_size if total_items > 0 else 1
        self.title("Xem trước Toàn bộ Danh bạ"); self.geometry("900x600")
        if icon_photo:
            try: self.iconphoto(True, icon_photo)
            except tk.TclError: pass
        self.transient(parent); self.grab_set()
        main_frame = ttk.Frame(self, padding=10); main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(0, weight=1); main_frame.columnconfigure(0, weight=1)
        self._create_treeview(main_frame); self._create_pagination_controls(main_frame); self.load_page()

    def _create_treeview(self, parent):
        tree_frame = ttk.Frame(parent); tree_frame.grid(row=0, column=0, sticky='nsew')
        self.columns_def = {key: name.replace('*', '') for key, name in self.columns_map.items()}
        self.tree = ttk.Treeview(tree_frame, columns=list(self.columns_def.keys()), show="headings")
        for key, name in self.columns_def.items():
            self.tree.heading(key, text=name); self.tree.column(key, width=120, anchor='w')
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y'); hsb.pack(side='bottom', fill='x'); self.tree.pack(side='left', fill='both', expand=True)
        self.tree.tag_configure('failed_row', background='#ffdddd', foreground='black')

    def _create_pagination_controls(self, parent):
        controls_frame = ttk.Frame(parent, padding=(0, 10, 0, 0)); controls_frame.grid(row=1, column=0, sticky='ew'); controls_frame.columnconfigure(2, weight=1)
        self.first_btn = ttk.Button(controls_frame, text="<< Đầu", command=lambda: self.go_to_page(1)); self.first_btn.grid(row=0, column=0, padx=2)
        self.prev_btn = ttk.Button(controls_frame, text="< Trước", command=self.prev_page); self.prev_btn.grid(row=0, column=1, padx=2)
        self.page_label_var = tk.StringVar()
        ttk.Label(controls_frame, textvariable=self.page_label_var, font=('Segoe UI', 10)).grid(row=0, column=2)
        self.next_btn = ttk.Button(controls_frame, text="Sau >", command=self.next_page); self.next_btn.grid(row=0, column=3, padx=2)
        self.last_btn = ttk.Button(controls_frame, text="Cuối >>", command=lambda: self.go_to_page(self.total_pages)); self.last_btn.grid(row=0, column=4, padx=2)
        
    def load_page(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for contact in self.db.get_contacts_paginated(self.current_page, self.page_size):
            values = [contact.get(key, '') for key in self.columns_def.keys()]
            self.tree.insert("", tk.END, values=values, tags=('failed_row' if contact['status'] == 'failed' else ''))
        self.update_controls()

    def update_controls(self):
        self.page_label_var.set(f"Trang {self.current_page} / {self.total_pages} (Tổng: {self.total_items} mục)")
        state = 'normal' if self.current_page > 1 else 'disabled'
        self.first_btn['state'] = self.prev_btn['state'] = state
        state = 'normal' if self.current_page < self.total_pages else 'disabled'
        self.next_btn['state'] = self.last_btn['state'] = state

    def go_to_page(self, page_num): self.current_page = page_num; self.load_page()
    def next_page(self):
        if self.current_page < self.total_pages: self.go_to_page(self.current_page + 1)
    def prev_page(self):
        if self.current_page > 1: self.go_to_page(self.current_page - 1)

# --- Điểm khởi chạy của ứng dụng ---
if __name__ == "__main__":
    root = tk.Tk(); root.withdraw()
    app_running = True
    try:
        app_icon = ImageTk.PhotoImage(Image.open(resource_path('icon.png')))
    except Exception as e:
        print(f"Lỗi tải hình ảnh: {e}"); app_icon = None

    def start_matrix():
        if app_running: MatrixWindow(root, on_complete=show_main_app)
    
    def start_system_check():
        if app_running: SystemCheckWindow(root, on_complete=start_matrix)

    def show_main_app():
        if not app_running: return
        root.deiconify()
        app_width, app_height = 750, 700
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        x = (screen_width - app_width) // 2
        start_y, end_y = -app_height, (screen_height - app_height) // 2
        root.geometry(f'{app_width}x{app_height}+{x}+{start_y}'); root.attributes('-alpha', 0.0)
        
        def animate_scroll(current_y, current_alpha):
            if not app_running: return
            if current_y < end_y:
                new_y = min(current_y + 25, end_y)
                new_alpha = min(current_alpha + 0.06, 1.0)
                root.geometry(f'{app_width}x{app_height}+{x}+{new_y}')
                root.attributes('-alpha', new_alpha)
                root.after(10, lambda: animate_scroll(new_y, new_alpha))
            else: root.attributes('-alpha', 1.0)
        
        ContactsApp(root, icon_photo=app_icon)
        animate_scroll(start_y, 0.0)
    
    start_system_check()
    root.mainloop()

    # *** SỬA LỖI KHI THOÁT TẠI ĐÂY ***
    # Bọc trong try-except để xử lý trường hợp cửa sổ đã bị hủy
    app_running = False
    try:
        if root.winfo_exists():
            root.destroy()
    except tk.TclError:
        pass # Bỏ qua lỗi nếu cửa sổ không còn tồn tại
