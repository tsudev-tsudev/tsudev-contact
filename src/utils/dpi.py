# -*- coding: utf-8 -*-
"""Bật nhận biết HiDPI trên Windows; các nền tảng khác bỏ qua an toàn."""
import ctypes


def enableHiDpiAwareness() -> None:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
