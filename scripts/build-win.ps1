# build-win.ps1 - Gói bản phát hành Windows x64 cho tsudev-contact.
# LƯU Ý: file này PHẢI lưu ở UTF-8 CÓ BOM - Windows PowerShell 5.1 đọc .ps1 không BOM
# theo bảng mã ANSI, làm hỏng chữ tiếng Việt và gây lỗi cú pháp khi chạy.
# Chạy từ thư mục gốc repo:  powershell -ExecutionPolicy Bypass -File scripts\build-win.ps1
# Tên file xuất ra do src/app_info.py quyết định (docs/DESIGN_SYSTEM.md mục 6).

[CmdletBinding()]
param(
    # Bỏ qua bước cài đặt phụ thuộc (dùng khi môi trường đã sẵn sàng).
    [switch]$SkipDeps,
    # Giữ lại thư mục build/ trung gian để chẩn đoán lỗi PyInstaller.
    [switch]$KeepBuild,
    # Ký số bản .exe sau khi build (xem scripts\sign-win.ps1 để biết giới hạn).
    [switch]$Sign,
    # Tham số chứng thư chuyển thẳng cho sign-win.ps1: -PfxPath / -Thumbprint / -SelfSigned.
    [string]$PfxPath,
    [string]$Thumbprint,
    [switch]$SelfSigned
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

# --- 1. Kiểm tra Python ---
$python = 'python'
if (-not (Get-Command $python -ErrorAction SilentlyContinue)) {
    throw "Không tìm thấy 'python' trong PATH. Cài Python 3.10+ rồi chạy lại."
}
Write-Step "Python: $(& $python --version)"

# --- 2. Phụ thuộc ---
if (-not $SkipDeps) {
    Write-Step 'Cài/nâng cấp phụ thuộc build (pyinstaller, pillow)'
    & $python -m pip install --upgrade --disable-pip-version-check pyinstaller pillow
    if ($LASTEXITCODE -ne 0) { throw 'Cài phụ thuộc thất bại.' }
}

# --- 3. Tên bản phát hành (nguồn duy nhất: src/app_info.py) ---
$releaseName = & $python -c "from src.app_info import RELEASE_BASENAME; print(RELEASE_BASENAME)"
if ($LASTEXITCODE -ne 0 -or -not $releaseName) { throw 'Không đọc được RELEASE_BASENAME từ src/app_info.py.' }
$releaseName = $releaseName.Trim()
Write-Step "Bản phát hành: $releaseName.exe"

# --- 4. Kiểm thử tối thiểu (AGENTS.md mục 3, checklist trước phát hành) ---
Write-Step 'Chạy test'
& $python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Test thất bại - dừng build.' }

# --- 5. Đóng gói ---
Write-Step 'PyInstaller'
& $python -m PyInstaller --noconfirm --clean Contacts.spec
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller thất bại.' }

# --- 6. Chuyển sản phẩm sang release/ ---
$built = Join-Path $repoRoot "dist\$releaseName.exe"
if (-not (Test-Path $built)) { throw "Không thấy sản phẩm build tại $built" }

$releaseDir = Join-Path $repoRoot 'release'
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
$final = Join-Path $releaseDir "$releaseName.exe"
Move-Item -Force $built $final

if (-not $KeepBuild) { Remove-Item -Recurse -Force (Join-Path $repoRoot 'build') -ErrorAction SilentlyContinue }

# --- 7. Ký số (tùy chọn) - phải ký TRƯỚC khi tính mã băm ---
if ($Sign -or $PfxPath -or $Thumbprint -or $SelfSigned) {
    Write-Step 'Ký số bản .exe'
    $signArgs = @{ Path = $final }
    if ($PfxPath)    { $signArgs['PfxPath'] = $PfxPath }
    if ($Thumbprint) { $signArgs['Thumbprint'] = $Thumbprint }
    if ($SelfSigned) { $signArgs['SelfSigned'] = $true }
    & (Join-Path $PSScriptRoot 'sign-win.ps1') @signArgs
}

# --- 8. Mã băm để người tải tự đối chiếu (cách xác thực MIỄN PHÍ, xem README.md) ---
Write-Step 'Tính SHA256SUMS.txt'
$hash = (Get-FileHash -Algorithm SHA256 $final).Hash.ToLower()
"$hash  $releaseName.exe" | Set-Content -Path (Join-Path $releaseDir 'SHA256SUMS.txt') -Encoding ascii
Write-Host "  $hash"

$sizeMb = [math]::Round((Get-Item $final).Length / 1MB, 1)
Write-Step "XONG: $final ($sizeMb MB)"
Write-Host 'Nhớ ghi 1 dòng vào CHANGELOG.md và tăng NN trong src/app_info.py cho bản kế tiếp.' -ForegroundColor Yellow
