# test-gui-win.ps1 — Chạy bộ kiểm thử GUI tự động trên Windows.
# LƯU Ý: file này PHẢI lưu ở UTF-8 CÓ BOM (xem đầu scripts/build-win.ps1).
# Chạy từ thư mục gốc repo:  powershell -ExecutionPolicy Bypass -File scripts\test-gui-win.ps1
# WSL không có tkinter/màn hình → tests/test_gui_smoke.py tự bỏ qua; chỉ script này chạy thật.

[CmdletBinding()]
param(
    # Chỉ chạy kiểm thử GUI, bỏ qua các test logic (đã chạy ở nơi khác).
    [switch]$GuiOnly
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

$python = 'python'
if (-not (Get-Command $python -ErrorAction SilentlyContinue)) {
    throw "Không tìm thấy 'python' trong PATH. Cài Python 3.10+ rồi chạy lại."
}
Write-Step "Python: $(& $python --version)"

& $python -c "import tkinter; tkinter.Tk().destroy()"
if ($LASTEXITCODE -ne 0) { throw 'Không mở được cửa sổ tkinter — cần phiên đồ họa (không chạy qua SSH/Session 0).' }

if ($GuiOnly) {
    Write-Step 'Chạy tests/test_gui_smoke.py'
    & $python -m unittest tests.test_gui_smoke -v
} else {
    Write-Step 'Chạy toàn bộ test (logic + GUI)'
    & $python -m unittest discover -s tests -v
}
if ($LASTEXITCODE -ne 0) { throw 'Kiểm thử thất bại.' }

Write-Step 'XONG: kiểm thử GUI đạt.'
