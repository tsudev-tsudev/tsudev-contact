# -*- coding: utf-8 -*-
"""Logic chuyển đổi CSV → vCard. Thuần túy, KHÔNG phụ thuộc tkinter.

Tiến trình và lỗi từng dòng được báo ra ngoài qua callback để lớp UI tự quyết
cách hiển thị (xem `src/features/csv_to_vcf/ui.py`).
"""
import csv
import unicodedata
from datetime import datetime

SKIP_OPTION = '(Bỏ qua)'

# Trường vCard hỗ trợ → nhãn hiển thị (dấu * = bắt buộc)
VCARD_FIELDS = {
    'name': 'Tên*',
    'number': 'SĐT*',
    'email': 'Email',
    'organization': 'Tổ chức',
    'address': 'Địa chỉ',
    'notes': 'Ghi chú',
    'birthday': 'Ngày sinh',
}

DB_FIELDS = ['name', 'number', 'email', 'organization', 'address', 'birthday', 'notes']

REQUIRED_FIELDS = ['name', 'number']

# Tên cột thường gặp trong file CSV xuất từ Google Contacts / Outlook / Excel tiếng Việt.
# Dùng để đoán ánh xạ cột — người dùng vẫn có thể chọn lại bằng tay.
FIELD_ALIASES = {
    'name': ['name', 'ten', 'hoten', 'fullname', 'displayname', 'contactname'],
    'number': ['number', 'phone', 'sdt', 'sodienthoai', 'dienthoai', 'mobile', 'tel', 'cell'],
    'email': ['email', 'mail', 'thudientu'],
    'organization': ['organization', 'org', 'company', 'congty', 'tochuc'],
    'address': ['address', 'diachi', 'addr'],
    'notes': ['notes', 'note', 'ghichu', 'comment'],
    'birthday': ['birthday', 'bday', 'ngaysinh', 'dob', 'birthdate'],
}

CSV_ENCODING = 'utf-8-sig'  # utf-8-sig để tự bỏ BOM do Excel sinh ra


def normalizeHeader(header: str) -> str:
    """Chuẩn hóa tên cột để so khớp: bỏ dấu tiếng Việt, hoa/thường, dấu cách và gạch nối."""
    noMarks = ''.join(
        c for c in unicodedata.normalize('NFD', header.lower().replace('đ', 'd'))
        if not unicodedata.combining(c)
    )
    return ''.join(c for c in noMarks if c.isalnum())


def guessHeader(field: str, headers: list, fallback: str) -> str:
    """Đoán cột CSV khớp với một trường vCard.

    Ưu tiên khớp đúng nguyên tên trước, sau đó mới khớp một phần (ví dụ cột
    "Phone 1 - Value" của Google Contacts). Không đoán được → trả `fallback`.
    """
    aliases = FIELD_ALIASES.get(field, [field])
    normalized = [(h, normalizeHeader(h)) for h in headers]
    for alias in aliases:
        for original, norm in normalized:
            if norm == alias:
                return original
    for alias in aliases:
        for original, norm in normalized:
            if alias in norm:
                return original
    return fallback


def readCsvHeaders(csvPath: str) -> list:
    """Đọc danh sách tên cột ở dòng đầu file CSV."""
    with open(csvPath, mode='r', encoding=CSV_ENCODING, newline='') as f:
        return next(csv.reader(f))


def countDataRows(csvPath: str) -> int:
    """Đếm số dòng dữ liệu (không tính dòng tiêu đề, bỏ qua dòng trống)."""
    with open(csvPath, 'r', encoding=CSV_ENCODING, errors='ignore') as f:
        return sum(1 for row in f if row.strip()) - 1


def buildVcard(contact) -> str:
    """Dựng một khối vCard 3.0 từ bản ghi liên hệ."""
    parts = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN;CHARSET=UTF-8:{contact['name']}",
        f"TEL;TYPE=CELL:{contact['number']}",
    ]
    if email := (contact['email'] or ''):
        parts.append(f"EMAIL:{email}")
    if org := (contact['organization'] or ''):
        parts.append(f"ORG;CHARSET=UTF-8:{org}")
    if addr := (contact['address'] or ''):
        parts.append(f"ADR;TYPE=HOME;CHARSET=UTF-8:;;{addr};;;;")
    if bday := (contact['birthday'] or ''):
        parts.append(f"BDAY:{bday}")
    if notes := (contact['notes'] or ''):
        escapedNotes = notes.replace('\n', '\\n')
        parts.append(f"NOTE;CHARSET=UTF-8:{escapedNotes}")
    parts.append(f"REV:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}")
    parts.append("END:VCARD")
    return "\n".join(parts) + "\n\n"


def importCsvToDb(csvPath, mappings, db, onProgress=None, onRowError=None) -> int:
    """Nạp toàn bộ CSV vào SQLite theo bảng ánh xạ cột. Trả về số dòng dữ liệu.

    `mappings`: {trường vCard: tên cột CSV} — giá trị SKIP_OPTION nghĩa là bỏ qua.
    `onProgress(rowIndex, totalRows)`, `onRowError(rowNumber)`: callback tùy chọn.
    """
    db.clearAllContacts()
    totalRows = countDataRows(csvPath)
    if totalRows <= 0:
        raise ValueError("File CSV rỗng hoặc chỉ có tiêu đề.")

    with open(csvPath, 'r', encoding=CSV_ENCODING, errors='ignore') as f:
        for i, row in enumerate(csv.DictReader(f)):
            data = {'original_row': i + 2}  # +2: bù dòng tiêu đề và chỉ số từ 1
            for field, csvHeader in mappings.items():
                if csvHeader != SKIP_OPTION:
                    data[field] = row.get(csvHeader, '')
            for field in DB_FIELDS:
                data.setdefault(field, '')

            # Ô trống trong CSV có thể là None → ép về chuỗi trước khi strip()
            isValid = all((data.get(field) or '').strip() for field in REQUIRED_FIELDS)
            data['status'] = 'success' if isValid else 'failed'
            if not isValid and onRowError:
                onRowError(i + 2)

            db.addContact(data)
            if onProgress:
                onProgress(i + 1, totalRows)

    return totalRows


def exportVcfFromDb(db, vcfPath, onProgress=None) -> int:
    """Ghi file .vcf từ các liên hệ hợp lệ trong CSDL. Trả về số liên hệ đã xuất."""
    contacts = db.getContactsPaginated(1, db.getContactCount())
    successfulContacts = [c for c in contacts if c['status'] == 'success']
    totalSuccess = len(successfulContacts)

    vcfContent = ""
    for i, contact in enumerate(successfulContacts):
        vcfContent += buildVcard(contact)
        if onProgress:
            onProgress(i + 1, totalSuccess)

    with open(vcfPath, 'w', encoding='utf-8') as f:
        f.write(vcfContent)
    return totalSuccess
