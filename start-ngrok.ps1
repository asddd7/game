$ErrorActionPreference = "Stop"

$projectDirectory = $PSScriptRoot
$phpPath = "C:\xampp\php\php.exe"
$port = 8000

if (-not (Test-Path -LiteralPath $phpPath)) {
    throw "PHP XAMPP tidak ditemukan di $phpPath."
}

$ngrokCommand = Get-Command "ngrok.cmd" -ErrorAction SilentlyContinue
if (-not $ngrokCommand) {
    throw "Perintah ngrok tidak ditemukan di PATH. Pastikan ngrok sudah terpasang."
}

$portProbe = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
try {
    $portProbe.Start()
}
catch {
    throw "Port $port sedang digunakan. Tutup aplikasi yang memakai port tersebut, lalu coba lagi."
}
finally {
    $portProbe.Stop()
}

$server = Start-Process `
    -FilePath $phpPath `
    -ArgumentList @("-S", "127.0.0.1:$port", "-t", $projectDirectory) `
    -PassThru `
    -WindowStyle Hidden

try {
    $serverReady = $false
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        if ($server.HasExited) {
            throw "PHP server berhenti sebelum siap."
        }

        try {
            $response = Invoke-WebRequest `
                -Uri "http://127.0.0.1:$port/" `
                -UseBasicParsing `
                -TimeoutSec 1
            if ($response.Content -notmatch "Langit Pagi") {
                throw "Server pada port $port tidak menyajikan game Langit Pagi."
            }
            $serverReady = $true
            break
        }
        catch {
            if ($_.Exception.Message -like "Server pada port*") {
                throw
            }
            Start-Sleep -Milliseconds 500
        }
    }

    if (-not $serverReady) {
        throw "PHP server tidak siap dalam 10 detik."
    }

    Write-Host "Game berjalan di http://127.0.0.1:$port/"
    Write-Host "Alamat publik ngrok akan muncul di bawah. Tekan Ctrl+C untuk menghentikan."
    & $ngrokCommand.Source http $port
    if ($LASTEXITCODE -ne 0) {
        throw "Ngrok keluar dengan kode $LASTEXITCODE. Pastikan akun ngrok sudah dikonfigurasi."
    }
}
finally {
    if (-not $server.HasExited) {
        Stop-Process -Id $server.Id -Force
    }
}
