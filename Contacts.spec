# -*- mode: python ; coding: utf-8 -*-
# Tên file xuất ra theo docs/DESIGN_SYSTEM.md mục 6 — lấy từ src/app_info.py (nguồn duy nhất).
import sys

sys.path.insert(0, SPECPATH)
from src.app_info import RELEASE_BASENAME

a = Analysis(
    ['contacts.pyw'],
    pathex=['.'],  # để bundle nhìn thấy package src/
    binaries=[],
    datas=[
        ('icon.png', '.'),
        # tokens/ là nguồn chân lý giao diện — src/services/tokens.py đọc lúc chạy
        ('tokens/design-tokens.json', 'tokens'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# Gói 1-file: sản phẩm phát hành là đúng 1 .exe mang tên theo quy ước.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=RELEASE_BASENAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
