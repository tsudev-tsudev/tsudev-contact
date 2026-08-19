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


if __name__ == '__main__':
    unittest.main()
