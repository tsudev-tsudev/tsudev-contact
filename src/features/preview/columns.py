# -*- coding: utf-8 -*-
"""Định nghĩa cột cho cửa sổ xem trước. Thuần túy, KHÔNG phụ thuộc tkinter."""
from src.features.csv_to_vcf.converter import VCARD_FIELDS

# Cột kỹ thuật luôn hiển thị ở đầu bảng, không đến từ ánh xạ CSV.
ROW_NUMBER_COLUMN = ('original_row', 'Dòng CSV', None)


def buildColumnDefs(previewColumns: dict, withRowNumber: bool = True) -> list:
    """`previewColumns` = {trường vCard: tên cột CSV nguồn} → [(khóa, nhãn vCard, cột CSV)].

    Nhãn lấy từ `VCARD_FIELDS` (đã bỏ dấu `*`) chứ không dùng tên cột CSV, để bảng
    xem trước đọc theo đúng ngôn ngữ vCard. Thứ tự cột theo `VCARD_FIELDS`.
    """
    defs = [ROW_NUMBER_COLUMN] if withRowNumber else []
    defs += [(field, label.replace('*', ''), previewColumns[field])
             for field, label in VCARD_FIELDS.items() if field in previewColumns]
    # Trường ngoài VCARD_FIELDS (nếu về sau có thêm) vẫn hiện, nhãn = tên trường.
    defs += [(field, field, header) for field, header in previewColumns.items()
             if field not in VCARD_FIELDS]
    return defs


def describeSources(columnDefs: list) -> str:
    """Chuỗi một dòng cho biết mỗi nhãn vCard lấy từ cột CSV nào."""
    pairs = [f"{label} ← {source}" for _, label, source in columnDefs if source]
    return "Nguồn dữ liệu:  " + "   ·   ".join(pairs) if pairs else ""
