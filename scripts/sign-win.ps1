# sign-win.ps1 — Ký số (Authenticode) bản .exe bằng công cụ CÓ SẴN trong Windows.
# LƯU Ý: file này PHẢI lưu ở UTF-8 CÓ BOM (xem đầu scripts/build-win.ps1).
#
# CHI PHÍ: script này KHÔNG dùng dịch vụ trả phí nào. Nhưng phải nói thẳng:
#   * Chứng thư TỰ KÝ (-SelfSigned) là miễn phí, ký được, đóng dấu thời gian được,
#     nhưng KHÔNG gỡ được cảnh báo SmartScreen trên máy người khác — vì máy đó không
#     tin chứng thư của mình. Nó chỉ hữu ích để kiểm thử quy trình ký, hoặc cho máy
#     nội bộ đã cài chứng thư (-TrustLocally).
#   * Muốn hết cảnh báo trên MỌI máy thì bắt buộc phải mua chứng thư OV/EV của CA
#     (khoảng vài triệu đồng/năm) — KHÔNG có phương án miễn phí tương đương.
#   * Cách miễn phí thay thế đang dùng: phát hành qua GitHub Releases kèm
#     SHA256SUMS.txt để người tải tự đối chiếu mã băm (xem README.md).
#
# Chạy:
#   powershell -ExecutionPolicy Bypass -File scripts\sign-win.ps1 -SelfSigned
#   powershell -ExecutionPolicy Bypass -File scripts\sign-win.ps1 -PfxPath C:\duong\dan\ma.pfx
#   powershell -ExecutionPolicy Bypass -File scripts\sign-win.ps1 -Thumbprint <dấu vân tay>
#
# MẬT KHẨU .pfx KHÔNG nhận qua tham số dòng lệnh (tránh lọt vào lịch sử lệnh / log):
# đặt biến môi trường $env:SIGN_PFX_PASSWORD, hoặc để script hỏi kín khi chạy.

[CmdletBinding()]
param(
    # File cần ký. Mặc định: release\<RELEASE_BASENAME>.exe
    [string]$Path,
    # Chứng thư .pfx do CA cấp (hoặc do mình xuất ra từ chứng thư tự ký).
    [string]$PfxPath,
    # Dấu vân tay chứng thư đã cài sẵn trong Cert:\CurrentUser\My
    [string]$Thumbprint,
    # Tạo (hoặc dùng lại) chứng thư tự ký MIỄN PHÍ — chỉ để kiểm thử, xem ghi chú đầu file.
    [switch]$SelfSigned,
    # Cài chứng thư tự ký vào kho tin cậy của NGƯỜI DÙNG HIỆN TẠI trên máy này.
    # Windows sẽ hiện hộp thoại hỏi xác nhận — phải bấm Yes, không tự động được.
    [switch]$TrustLocally,
    # Máy chủ đóng dấu thời gian RFC3161 (miễn phí, không cần tài khoản).
    [string]$TimestampUrl = 'http://timestamp.digicert.com'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

$SELF_SIGNED_SUBJECT = 'CN=tsudev (self-signed, khong danh cho phat hanh cong khai)'

# --- 1. Xác định file cần ký ---
if (-not $Path) {
    $releaseName = (& python -c "from src.app_info import RELEASE_BASENAME; print(RELEASE_BASENAME)").Trim()
    if (-not $releaseName) { throw 'Không đọc được RELEASE_BASENAME từ src/app_info.py.' }
    $Path = Join-Path $repoRoot "release\$releaseName.exe"
}
if (-not (Test-Path $Path)) { throw "Không thấy file cần ký: $Path (chạy scripts\build-win.ps1 trước)." }
Write-Step "File: $Path"

# --- 2. Lấy chứng thư ---
$cert = $null
if ($PfxPath) {
    if (-not (Test-Path $PfxPath)) { throw "Không thấy file chứng thư: $PfxPath" }
    $password = if ($env:SIGN_PFX_PASSWORD) {
        ConvertTo-SecureString $env:SIGN_PFX_PASSWORD -AsPlainText -Force
    } else {
        Read-Host -Prompt 'Mật khẩu file .pfx' -AsSecureString
    }
    $cert = Get-PfxCertificate -FilePath $PfxPath -Password $password
} elseif ($Thumbprint) {
    $cert = Get-Item "Cert:\CurrentUser\My\$Thumbprint" -ErrorAction SilentlyContinue
    if (-not $cert) { throw "Không thấy chứng thư $Thumbprint trong Cert:\CurrentUser\My" }
} elseif ($SelfSigned) {
    $cert = Get-ChildItem Cert:\CurrentUser\My |
        Where-Object { $_.Subject -eq $SELF_SIGNED_SUBJECT -and $_.NotAfter -gt (Get-Date) } |
        Select-Object -First 1
    if ($cert) {
        Write-Step "Dùng lại chứng thư tự ký sẵn có: $($cert.Thumbprint)"
    } else {
        Write-Step 'Tạo chứng thư tự ký mới (miễn phí, hết hạn sau 3 năm)'
        $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject $SELF_SIGNED_SUBJECT `
            -CertStoreLocation Cert:\CurrentUser\My -KeyAlgorithm RSA -KeyLength 3072 `
            -HashAlgorithm SHA256 -NotAfter (Get-Date).AddYears(3)
    }
    if ($TrustLocally) {
        Write-Step 'Cài chứng thư vào Cert:\CurrentUser\Root (chỉ có tác dụng trên máy này)'
        Write-Host '  Windows sẽ hỏi xác nhận cài chứng thư gốc — bấm Yes thì mới có hiệu lực.' -ForegroundColor Yellow
        $exported = Join-Path $env:TEMP 'tsudev-selfsigned.cer'
        Export-Certificate -Cert $cert -FilePath $exported | Out-Null
        Import-Certificate -FilePath $exported -CertStoreLocation Cert:\CurrentUser\Root | Out-Null
        Remove-Item $exported -Force
    }
} else {
    throw 'Chưa chọn chứng thư. Dùng -PfxPath, -Thumbprint hoặc -SelfSigned (xem ghi chú đầu file).'
}

# --- 3. Ký + đóng dấu thời gian ---
Write-Step "Ký bằng chứng thư: $($cert.Subject)"
$result = Set-AuthenticodeSignature -FilePath $Path -Certificate $cert `
    -HashAlgorithm SHA256 -TimestampServer $TimestampUrl
if ($result.Status -ne 'Valid' -and $result.Status -ne 'UnknownError') {
    throw "Ký thất bại: $($result.Status) — $($result.StatusMessage)"
}

# --- 4. Kiểm chứng ---
$check = Get-AuthenticodeSignature -FilePath $Path
Write-Step "Trạng thái chữ ký: $($check.Status)"
Write-Host "  Người ký      : $($check.SignerCertificate.Subject)"
Write-Host "  Dấu thời gian : $(if ($check.TimeStamperCertificate) { 'có' } else { 'KHÔNG (máy chủ timestamp không phản hồi)' })"

if ($check.Status -eq 'UnknownError' -or $SelfSigned) {
    Write-Host ''
    Write-Host 'NHẮC LẠI: chữ ký tự ký KHÔNG gỡ được cảnh báo SmartScreen trên máy người khác.' -ForegroundColor Yellow
    Write-Host 'Bản phát hành công khai vẫn nên đối chiếu qua release\SHA256SUMS.txt.' -ForegroundColor Yellow
}
