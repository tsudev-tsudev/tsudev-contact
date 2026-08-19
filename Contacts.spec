# -*- mode: python ; coding: utf-8 -*-


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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Contacts',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Contacts',
)
