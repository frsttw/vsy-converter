$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$vendorDir = Join-Path $projectDir 'vendor'
$imageMagickInstaller = Join-Path $vendorDir 'ImageMagick-installer.exe'
$imageMagickUrl = 'https://github.com/ImageMagick/ImageMagick/releases/download/7.1.2-29/ImageMagick-7.1.2-29-Q16-HDRI-x64-dll.exe'
$ffmpegExe = Join-Path $vendorDir 'ffmpeg.exe'
$ffmpegUrl = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'

New-Item -ItemType Directory -Force -Path $vendorDir | Out-Null
if (-not (Test-Path -LiteralPath $imageMagickInstaller)) {
    Invoke-WebRequest -Uri $imageMagickUrl -OutFile $imageMagickInstaller
}
if (-not (Test-Path -LiteralPath $ffmpegExe)) {
    $ffmpegZip = Join-Path $vendorDir 'ffmpeg.zip'
    $ffmpegExtract = Join-Path $vendorDir 'ffmpeg-extract'
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip
    Expand-Archive -LiteralPath $ffmpegZip -DestinationPath $ffmpegExtract -Force
    $downloadedFfmpeg = Get-ChildItem -LiteralPath $ffmpegExtract -Recurse -Filter 'ffmpeg.exe' | Select-Object -First 1
    if (-not $downloadedFfmpeg) { throw 'FFmpeg não foi encontrado no pacote baixado.' }
    Copy-Item -LiteralPath $downloadedFfmpeg.FullName -Destination $ffmpegExe
    Remove-Item -LiteralPath $ffmpegZip
    Remove-Item -LiteralPath $ffmpegExtract -Recurse
}

Push-Location $projectDir
try {
    py -m PyInstaller --noconfirm --clean --onefile --windowed --icon .\assets\vs-conversor.ico --add-data 'assets\vs-conversor.ico;assets' --add-data 'assets\vs-conversor.png;assets' --name 'Vsy Converter' .\app.py
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao empacotar o aplicativo.' }

    $compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
    if (-not (Test-Path -LiteralPath $compiler)) {
        $compiler = Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe'
    }
    if (-not (Test-Path -LiteralPath $compiler)) {
        $compiler = Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe'
    }
    if (-not (Test-Path -LiteralPath $compiler)) {
        throw 'Inno Setup 6 não foi encontrado.'
    }
    & $compiler .\installer.iss
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar o instalador.' }
}
finally {
    Pop-Location
}
