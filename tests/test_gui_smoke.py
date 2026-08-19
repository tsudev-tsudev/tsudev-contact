# -*- coding: utf-8 -*-
"""Kiểm thử GUI tự động — bản tự động hóa kịch bản `docs/ARCHITECTURE.md` mục 8.

Chạy được ở đâu: máy có tkinter + phiên đồ họa (Windows, hoặc Linux có X/Xvfb).
Không có màn hình → toàn bộ test tự bỏ qua, KHÔNG làm đỏ bộ test chung.

    python -m unittest discover -s tests          # WSL: skip
    scripts/test-gui-win.ps1                      # Windows: chạy thật

Test không bấm chuột thật: nó gọi thẳng handler của widget và tự quay vòng lặp sự
kiện (`pump`), nên chạy được cả trên runner CI mà vẫn đi đúng đường code của UI.
"""
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import tkinter as tk
except ImportError:  # WSL không cài python3-tk
    tk = None

CSV_SAMPLE = """Full Name,Phone 1 - Value,E-mail,Ghi chú
Nguyễn Văn A,0900000001,a@example.com,Ghi chú A
,0900000002,,Thiếu tên
Trần Thị B,,b@example.com,Thiếu số
Lê Văn C,0900000003,,
"""
VALID_CONTACTS = 2
FAILED_ROWS = [3, 4]
PUMP_TICK_SECONDS = 0.02
DEFAULT_TIMEOUT_SECONDS = 30
LAUNCH_TIMEOUT_SECONDS = 40  # chuỗi splash ~6,5s, cộng dư cho runner CI chậm


def _hasDisplay() -> bool:
    if tk is None:
        return False
    try:
        probe = tk.Tk()
    except Exception:
        return False
    probe.destroy()
    return True


HAS_GUI = _hasDisplay()
SKIP_REASON = "Không có tkinter hoặc phiên đồ họa — bỏ qua kiểm thử GUI"

_tempRoot = None
_originalTempdir = None


def setUpModule():
    """Ép mọi dữ liệu app (settings.json, CSDL tạm) vào thư mục dùng một lần."""
    global _tempRoot, _originalTempdir
    _tempRoot = tempfile.TemporaryDirectory()
    _originalTempdir = tempfile.tempdir
    tempfile.tempdir = _tempRoot.name


def tearDownModule():
    tempfile.tempdir = _originalTempdir
    _tempRoot.cleanup()


class DialogRecorder:
    """Thay `messagebox` để hộp thoại không chặn vòng lặp test."""

    def __init__(self):
        self.calls = []

    def _record(self, kind):
        def handler(title, message, **kwargs):
            self.calls.append((kind, title, message))
            return 'ok'
        return handler

    def __getattr__(self, name):
        return self._record(name)

    def titles(self, kind=None):
        return [t for k, t, _ in self.calls if kind is None or k == kind]

    def messages(self):
        return "\n".join(m for _, _, m in self.calls)


def pump(widget, seconds=0.1):
    """Quay vòng lặp sự kiện tkinter trong `seconds` giây."""
    end = time.time() + seconds
    while time.time() < end:
        widget.update()
        time.sleep(PUMP_TICK_SECONDS)


def waitFor(widget, predicate, timeout=DEFAULT_TIMEOUT_SECONDS):
    """Quay vòng lặp cho tới khi `predicate()` đúng. Trả False nếu hết giờ."""
    end = time.time() + timeout
    while time.time() < end:
        widget.update()
        if predicate():
            return True
        time.sleep(PUMP_TICK_SECONDS)
    return False


@unittest.skipUnless(HAS_GUI, SKIP_REASON)
class GuiScenarioTest(unittest.TestCase):
    """Mỗi test tự dựng cửa sổ riêng để chạy độc lập, không phụ thuộc thứ tự."""

    def setUp(self):
        from src.features.csv_to_vcf import ui as csvUi

        self.workDir = tempfile.TemporaryDirectory()
        self.csvPath = os.path.join(self.workDir.name, 'danh-ba.csv')
        self.vcfPath = os.path.join(self.workDir.name, 'danh-ba.vcf')
        with open(self.csvPath, 'w', encoding='utf-8-sig') as f:
            f.write(CSV_SAMPLE)

        self.dialogs = DialogRecorder()
        self._originalMessagebox = csvUi.messagebox
        csvUi.messagebox = self.dialogs

        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        from src.features.csv_to_vcf import ui as csvUi

        csvUi.messagebox = self._originalMessagebox
        try:
            self.root.destroy()
        except tk.TclError:
            pass
        self.workDir.cleanup()

    # ------------------------------------------------------------- tiện ích
    def makeApp(self, theme='light'):
        from src.features.csv_to_vcf.ui import ContactsApp
        from src.services import settings

        settings.saveSetting('theme', theme)
        app = ContactsApp(self.root, iconPhoto=None)
        self.root.deiconify()
        pump(self.root, 0.2)
        return app

    def runConversion(self, app):
        app.csvPathVar.set(self.csvPath)
        app.vcfPathVar.set(self.vcfPath)
        app._loadCsvHeaders()
        pump(self.root, 0.1)
        app._startConversion()
        done = waitFor(self.root, lambda: str(app.convertButton['state']) == 'normal')
        self.assertTrue(done, "Chuyển đổi không kết thúc trong thời gian cho phép")
        pump(self.root, 0.2)  # chờ callback `after` cuối cùng chạy nốt
        return app

    def logText(self, app):
        return app.statusLog.get('1.0', tk.END)

    # -------------------------------------------------- kịch bản mục 8 (2)
    def test_chuoi_khoi_dong_len_den_cua_so_chinh(self):
        from src.app_info import APP_VERSION
        from src.main.app import AppLauncher

        launcher = AppLauncher(self.root, iconPhoto=None)
        launcher.start()
        reached = waitFor(self.root, lambda: APP_VERSION in self.root.title(),
                          timeout=LAUNCH_TIMEOUT_SECONDS)
        launcher.isRunning = False
        self.assertTrue(reached, "Không tới được cửa sổ chính sau chuỗi splash")
        pump(self.root, 0.3)
        self.assertEqual(self.root.state(), 'normal')  # đã deiconify, không còn ẩn

    # -------------------------------------------------- kịch bản mục 8 (3)
    def test_doan_du_7_truong_khong_con_bo_qua_o_truong_bat_buoc(self):
        from src.features.csv_to_vcf.converter import REQUIRED_FIELDS, SKIP_OPTION, VCARD_FIELDS

        app = self.makeApp()
        app.csvPathVar.set(self.csvPath)
        app._loadCsvHeaders()
        pump(self.root, 0.1)

        self.assertEqual(set(app.fieldMappings), set(VCARD_FIELDS))
        for field in REQUIRED_FIELDS:
            self.assertNotEqual(app.fieldMappings[field].get(), SKIP_OPTION,
                                f"Trường bắt buộc '{field}' không được đoán ra cột CSV")
        self.assertEqual(app.fieldMappings['number'].get(), 'Phone 1 - Value')

    # -------------------------------------------------- kịch bản mục 8 (4)
    def test_chuyen_doi_bao_dong_loi_va_xuat_dung_so_lien_he(self):
        app = self.runConversion(self.makeApp())

        log = self.logText(app)
        for row in FAILED_ROWS:
            self.assertIn(f"Lỗi dòng {row}", log)
        self.assertTrue(app.statusLog.tag_ranges('error'), "Dòng lỗi phải được tô màu danger")
        self.assertIn("Thành công", self.dialogs.titles('showinfo'))

        with open(self.vcfPath, encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content.count("BEGIN:VCARD"), VALID_CONTACTS)
        self.assertIn("FN;CHARSET=UTF-8:Nguyễn Văn A", content)
        self.assertNotIn("0900000002", content)  # dòng thiếu tên không được xuất

    # -------------------------------------------------- kịch bản mục 8 (5)
    def test_xem_truoc_dung_nhan_vcard_va_to_do_dong_loi(self):
        from src.features.preview.ui import PreviewWindow

        app = self.runConversion(self.makeApp())
        app._showPreviewDialog()
        pump(self.root, 0.3)

        previews = [w for w in self.root.winfo_children() if isinstance(w, PreviewWindow)]
        self.assertEqual(len(previews), 1)
        preview = previews[0]

        headings = [preview.tree.heading(key)['text'] for key in preview.columnKeys]
        self.assertEqual(headings, ['Dòng CSV', 'Tên', 'SĐT', 'Email', 'Ghi chú'])
        for csvHeader in ('Full Name', 'Phone 1 - Value', 'E-mail'):
            self.assertNotIn(csvHeader, headings, "Tiêu đề cột phải là nhãn vCard, không phải cột CSV")

        rows = preview.tree.get_children()
        self.assertEqual(len(rows), 4)
        failed = [r for r in rows if 'failed_row' in preview.tree.item(r, 'tags')]
        self.assertEqual(len(failed), len(FAILED_ROWS))
        self.assertIn("Tổng: 4 mục", preview.pageLabelVar.get())
        preview.destroy()

    # -------------------------------------------------- kịch bản mục 8 (6)
    def test_doi_chu_de_khong_mat_chu_va_duoc_ghi_nho(self):
        from src.services import settings
        from src.services.tokens import loadTokens

        app = self.makeApp()
        for themeName in settings.THEMES:
            app._applyTheme(themeName)
            pump(self.root, 0.2)
            tokens = loadTokens(themeName)

            self.assertEqual(self.root['bg'], tokens.color('bg-base'))
            button = app.convertButton
            self.assertTrue(button['text'].strip(), "Nút chính không được mất chữ")
            self.assertEqual(button['bg'], tokens.color('primary'))
            self.assertEqual(button['fg'], tokens.color('on-primary'))
            self.assertNotEqual(button['bg'], button['fg'])
            self.assertEqual(app.statusLog['bg'], tokens.color('bg-surface'))
            self.assertEqual(settings.loadSettings()['theme'], themeName)


if __name__ == '__main__':
    unittest.main()
