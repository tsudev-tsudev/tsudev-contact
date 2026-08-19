# -*- coding: utf-8 -*-
"""Test định nghĩa cột cửa sổ xem trước (nhãn vCard, không phải tên cột CSV)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.features.preview.columns import buildColumnDefs, describeSources

PREVIEW_COLUMNS = {'notes': 'Ghi chú CSV', 'number': 'Phone 1 - Value', 'name': 'Full Name'}


class PreviewColumnsTest(unittest.TestCase):
    def test_tieu_de_dung_nhan_vcard_va_dung_thu_tu(self):
        defs = buildColumnDefs(PREVIEW_COLUMNS)
        self.assertEqual([label for _, label, _ in defs],
                         ['Dòng CSV', 'Tên', 'SĐT', 'Ghi chú'])
        self.assertEqual([key for key, _, _ in defs],
                         ['original_row', 'name', 'number', 'notes'])

    def test_nhan_bat_buoc_bo_dau_sao(self):
        labels = [label for _, label, _ in buildColumnDefs(PREVIEW_COLUMNS)]
        self.assertFalse(any('*' in label for label in labels))

    def test_bo_cot_so_dong_khi_khong_can(self):
        defs = buildColumnDefs(PREVIEW_COLUMNS, withRowNumber=False)
        self.assertEqual([key for key, _, _ in defs], ['name', 'number', 'notes'])

    def test_truong_khong_duoc_anh_xa_thi_khong_co_cot(self):
        keys = [key for key, _, _ in buildColumnDefs(PREVIEW_COLUMNS)]
        self.assertNotIn('email', keys)

    def test_chu_thich_nguon_ghep_nhan_voi_cot_csv(self):
        caption = describeSources(buildColumnDefs(PREVIEW_COLUMNS))
        self.assertIn('SĐT ← Phone 1 - Value', caption)
        self.assertIn('Tên ← Full Name', caption)
        self.assertNotIn('Dòng CSV ←', caption)  # cột kỹ thuật không có nguồn CSV

    def test_khong_co_cot_nao_thi_chu_thich_rong(self):
        self.assertEqual(describeSources(buildColumnDefs({}, withRowNumber=False)), '')
