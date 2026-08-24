# -*- coding: utf-8 -*-
"""Tùy chọn người dùng (chủ đề giao diện...) lưu trong thư mục dữ liệu tạm của ứng dụng.

KHÔNG lưu cạnh file thực thi: thư mục cài đặt có thể chỉ-đọc (xem docs/ARCHITECTURE.md).
File này chỉ chứa tùy chọn hiển thị - tuyệt đối không chứa dữ liệu danh bạ.
"""
import json
import os
import tempfile

APP_DIRNAME = 'tsudev-contact'
SETTINGS_FILE = 'settings.json'
THEMES = ('light', 'warm', 'dark')
THEME_LABELS = {'light': 'Sáng', 'warm': 'Ấm', 'dark': 'Tối'}
DEFAULT_SETTINGS = {'theme': 'light'}


def appDataDir() -> str:
    """Thư mục dữ liệu tạm của ứng dụng trong temp người dùng (tự tạo nếu chưa có)."""
    path = os.path.join(tempfile.gettempdir(), APP_DIRNAME)
    os.makedirs(path, exist_ok=True)
    return path


def settingsPath() -> str:
    return os.path.join(appDataDir(), SETTINGS_FILE)


def loadSettings(path: str = None) -> dict:
    """Đọc tùy chọn; file hỏng/thiếu → trả mặc định (không bao giờ ném lỗi ra UI)."""
    settings = dict(DEFAULT_SETTINGS)
    try:
        with open(path or settingsPath(), 'r', encoding='utf-8') as f:
            stored = json.load(f)
        if isinstance(stored, dict):
            settings.update({k: v for k, v in stored.items() if k in DEFAULT_SETTINGS})
    except (OSError, ValueError):
        pass
    if settings['theme'] not in THEMES:
        settings['theme'] = DEFAULT_SETTINGS['theme']
    return settings


def saveSetting(key: str, value, path: str = None) -> None:
    """Ghi 1 tùy chọn. Lỗi ghi (đĩa đầy, chỉ-đọc) chỉ làm mất tùy chọn, không làm sập app."""
    if key not in DEFAULT_SETTINGS:
        raise KeyError(f"Tùy chọn không hợp lệ: {key}")
    target = path or settingsPath()
    settings = loadSettings(target)
    settings[key] = value
    try:
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except OSError:
        pass
