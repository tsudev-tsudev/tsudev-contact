# -*- coding: utf-8 -*-
"""Thông tin định danh ứng dụng — khai báo một nơi duy nhất."""

APP_NAME = "Contacts"
APP_SLUG = "tsudev-contact"
# Quy ước: docs/DESIGN_SYSTEM.md mục 6 — {YY}.{M}.{DD}{NN}
# (26.8.2001 = bản phát hành thứ 01 ngày 20/08/2026). Bản trước quy ước: "5.2".
APP_VERSION = "26.8.2001"
APP_ARCH = "x64"
APP_AUTHOR = "nguyentrangtinhsu"
SUPPORT_URL = "https://www.facebook.com/nguyentrangtinhsu"

# Tên file phát hành (không phần mở rộng) — dùng cho PyInstaller và scripts/build-win.ps1.
RELEASE_BASENAME = f"{APP_SLUG}_{APP_VERSION}_{APP_ARCH}-setup"
