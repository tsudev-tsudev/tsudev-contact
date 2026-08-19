# -*- coding: utf-8 -*-
"""Giải đường dẫn tài nguyên cho cả môi trường dev lẫn bundle PyInstaller."""
import os
import sys


def resourcePath(relativePath: str) -> str:
    """Trả về đường dẫn tuyệt đối tới tài nguyên đi kèm ứng dụng."""
    try:
        basePath = sys._MEIPASS
    except AttributeError:
        basePath = os.path.abspath(".")
    return os.path.join(basePath, relativePath)
