# -*- coding: utf-8 -*-
"""Test tích hợp luồng CSV → SQLite → vCard. Chỉ dùng thư viện chuẩn.

Chạy: python -m unittest discover -s tests
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.features.csv_to_vcf import converter
from src.services import settings
from src.services.database import DatabaseManager

CSV_SAMPLE = """Tên,SĐT,Ghi chú,Email
Nguyễn Văn A,0900000001,Ghi chú A,a@example.com
,0900000002,Thiếu tên,
Trần Thị B,,Thiếu số,
Lê Văn C,0900000003,,
"""

MAPPINGS = {
    'name': 'Tên', 'number': 'SĐT', 'notes': 'Ghi chú', 'email': 'Email',
    'organization': converter.SKIP_OPTION,
    'address': converter.SKIP_OPTION,
    'birthday': converter.SKIP_OPTION,
}


class CsvToVcfTest(unittest.TestCase):
    def setUp(self):
        self.tempDir = tempfile.TemporaryDirectory()
        self.csvPath = os.path.join(self.tempDir.name, 'danh-ba.csv')
        self.vcfPath = os.path.join(self.tempDir.name, 'danh-ba.vcf')
        with open(self.csvPath, 'w', encoding='utf-8-sig') as f:
            f.write(CSV_SAMPLE)
        self.db = DatabaseManager(os.path.join(self.tempDir.name, 'test.db'))

    def tearDown(self):
        self.tempDir.cleanup()

    def test_dem_dong_du_lieu(self):
        self.assertEqual(converter.countDataRows(self.csvPath), 4)

    def test_doc_header(self):
        self.assertEqual(converter.readCsvHeaders(self.csvPath),
                         ['Tên', 'SĐT', 'Ghi chú', 'Email'])

    def test_nap_csv_danh_dau_dong_thieu_truong_bat_buoc(self):
        errorRows = []
        totalRows = converter.importCsvToDb(self.csvPath, MAPPINGS, self.db,
                                            onRowError=errorRows.append)
        self.assertEqual(totalRows, 4)
        self.assertEqual(self.db.getContactCount(), 4)
        self.assertEqual(errorRows, [3, 4])  # dòng 3 thiếu tên, dòng 4 thiếu số

    def test_xuat_vcf_chi_gom_lien_he_hop_le(self):
        converter.importCsvToDb(self.csvPath, MAPPINGS, self.db)
        totalSuccess = converter.exportVcfFromDb(self.db, self.vcfPath)
        self.assertEqual(totalSuccess, 2)

        with open(self.vcfPath, encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content.count("BEGIN:VCARD"), 2)
        self.assertIn("FN;CHARSET=UTF-8:Nguyễn Văn A", content)
        self.assertIn("TEL;TYPE=CELL:0900000001", content)
        self.assertIn("EMAIL:a@example.com", content)
        self.assertNotIn("Thiếu tên", content)
        self.assertNotIn("Thiếu số", content)

    def test_bo_qua_cot_khong_ghep_noi(self):
        converter.importCsvToDb(self.csvPath, MAPPINGS, self.db)
        converter.exportVcfFromDb(self.db, self.vcfPath)
        with open(self.vcfPath, encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn("ORG;", content)
        self.assertNotIn("ADR;", content)

    def test_buildVcard_thoat_xuong_dong_trong_ghi_chu(self):
        contact = {'name': 'A', 'number': '01', 'email': '', 'organization': '',
                   'address': '', 'birthday': '', 'notes': 'dòng 1\ndòng 2'}
        vcard = converter.buildVcard(contact)
        self.assertIn(r"NOTE;CHARSET=UTF-8:dòng 1\ndòng 2", vcard)
        self.assertNotIn("dòng 1\ndòng 2", vcard)

    def test_o_trong_la_None_khong_lam_hong_luong_xu_ly(self):
        """sqlite3.Row không có .get(); ô rỗng trả None — cả hai từng gây lỗi."""
        converter.importCsvToDb(self.csvPath, MAPPINGS, self.db)
        rows = self.db.getContactsPaginated(1, 10)
        self.assertFalse(hasattr(rows[0], 'get'))
        values = [row['organization'] or '' for row in rows]
        self.assertEqual(values, ['', '', '', ''])

    def test_csv_chi_co_tieu_de_bao_loi_ro_rang(self):
        emptyCsv = os.path.join(self.tempDir.name, 'rong.csv')
        with open(emptyCsv, 'w', encoding='utf-8-sig') as f:
            f.write("Tên,SĐT\n")
        with self.assertRaises(ValueError):
            converter.importCsvToDb(emptyCsv, MAPPINGS, self.db)


class GuessHeaderTest(unittest.TestCase):
    """Đoán cột CSV → trường vCard (converter.guessHeader)."""

    SKIP = converter.SKIP_OPTION

    def test_khop_dung_ten_cot_tieng_anh(self):
        headers = ['Name', 'Phone', 'Email', 'Organization', 'Address', 'Note', 'Birthday']
        guessed = {f: converter.guessHeader(f, headers, self.SKIP) for f in converter.VCARD_FIELDS}
        self.assertEqual(guessed, {
            'name': 'Name', 'number': 'Phone', 'email': 'Email',
            'organization': 'Organization', 'address': 'Address',
            'notes': 'Note', 'birthday': 'Birthday'})

    def test_khop_ten_cot_tieng_viet_va_co_dau_cach(self):
        headers = ['Họ tên', 'Số điện thoại', 'Địa chỉ', 'Ghi chú']
        self.assertEqual(converter.guessHeader('address', headers, self.SKIP), 'Địa chỉ')
        self.assertEqual(converter.guessHeader('notes', headers, self.SKIP), 'Ghi chú')

    def test_khop_mot_phan_kieu_google_contacts(self):
        headers = ['First Name', 'Phone 1 - Value', 'E-mail 1 - Value']
        self.assertEqual(converter.guessHeader('number', headers, self.SKIP), 'Phone 1 - Value')
        self.assertEqual(converter.guessHeader('email', headers, self.SKIP), 'E-mail 1 - Value')

    def test_uu_tien_khop_nguyen_ten_truoc_khop_mot_phan(self):
        headers = ['Mobile Phone', 'Phone']
        self.assertEqual(converter.guessHeader('number', headers, self.SKIP), 'Phone')

    def test_khong_doan_duoc_thi_tra_gia_tri_mac_dinh(self):
        self.assertEqual(converter.guessHeader('birthday', ['Cột lạ'], self.SKIP), self.SKIP)


class SettingsTest(unittest.TestCase):
    """Tùy chọn người dùng (src/services/settings.py)."""

    def setUp(self):
        self.tempDir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tempDir.name, 'settings.json')

    def tearDown(self):
        self.tempDir.cleanup()

    def test_chua_co_file_thi_tra_mac_dinh(self):
        self.assertEqual(settings.loadSettings(self.path), {'theme': 'light'})

    def test_ghi_roi_doc_lai_dung_chu_de(self):
        settings.saveSetting('theme', 'dark', self.path)
        self.assertEqual(settings.loadSettings(self.path)['theme'], 'dark')

    def test_file_hong_khong_lam_sap_app(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write('{ khong phai json')
        self.assertEqual(settings.loadSettings(self.path)['theme'], 'light')

    def test_chu_de_la_bo_ve_mac_dinh(self):
        settings.saveSetting('theme', 'neon', self.path)
        self.assertEqual(settings.loadSettings(self.path)['theme'], 'light')

    def test_khoa_tuy_chon_khong_hop_le_bi_tu_choi(self):
        with self.assertRaises(KeyError):
            settings.saveSetting('mat_khau', 'x', self.path)


if __name__ == '__main__':
    unittest.main()
