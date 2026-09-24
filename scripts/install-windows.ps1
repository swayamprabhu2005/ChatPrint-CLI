# AI Conversation CLI - Windows Installer & Python 3.10.8 Bootstrapper
# Requires PowerShell 5.1+

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "          AI Conversation CLI Setup               " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Architecture Check
$Arch = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
Write-Host "Checking system architecture... Detected: Windows $Arch" -ForegroundColor Gray

# 2. Check Python 3.10.8
$TargetVersion = "3.10.8"
$FoundPython = $null

# Check available Python interpreters
$Candidates = @(
    "python",
    "py -3.10-64",
    "py -3.10",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "D:\MyPrograms\Python\python.exe",
    "C:\Python310\python.exe"
)

foreach ($cmd in $Candidates) {
    try {
        $vOutput = & (Get-Command $cmd.Split(' ')[0] -ErrorAction SilentlyContinue) $cmd.Split(' ')[1..($cmd.Split(' ').Length-1)] -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
        if ($vOutput -eq $TargetVersion) {
            $FoundPython = $cmd
            break
        }
    } catch {}
}

if ($FoundPython) {
    Write-Host "✓ Python $TargetVersion detected ($FoundPython)" -ForegroundColor Green
    $PythonExe = $FoundPython
} else {
    Write-Host "Python $TargetVersion was not detected on this system." -ForegroundColor Yellow
    Write-Host "AI Conversation CLI recommends Python $TargetVersion for stability."
    $Choice = Read-Host "Download official Python $TargetVersion installer from python.org? [Y/n]"
    if ($Choice -ne "" -and $Choice -notmatch "^[yY]") {
        Write-Host "Installation aborted. Please install Python 3.10.8 and rerun setup." -ForegroundColor Red
        exit 1
    }

    # Download from official Python release mirror
    $Url = "https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe"
    $ExpectedHash = "6b896b0fd01e8cffadcf2fd75a9fe847248e5828ae8f92167812ec1e57c6b90f"
    $TempInstaller = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "python-3.10.8-amd64.exe")

    Write-Host "Downloading Python $TargetVersion from official source: $Url" -ForegroundColor Cyan
    Invoke-WebRequest -Uri $Url -OutFile $TempInstaller

    # Verify Cryptographic Checksum
    Write-Host "Verifying SHA-256 checksum..." -ForegroundColor Gray
    $ActualHash = (Get-FileHash -Path $TempInstaller -Algorithm SHA256).Hash.ToLower()
    if ($ActualHash -ne $ExpectedHash) {
        Write-Host "Security Error: Checksum verification failed! File may be corrupted or tampered." -ForegroundColor Red
        Remove-Item -Force $TempInstaller
        exit 1
    }
    Write-Host "✓ SHA-256 checksum verified ($ActualHash)" -ForegroundColor Green

    # Install into private directory without global interference
    $PrivatePythonDir = "$env:LOCALAPPDATA\AIConversationCLI\runtime"
    Write-Host "Installing Python into private runtime: $PrivatePythonDir" -ForegroundColor Cyan
    Start-Process -FilePath $TempInstaller -ArgumentList "/quiet InstallAllUsers=0 TargetDir=`"$PrivatePythonDir`" PrependPath=0" -Wait
    Remove-Item -Force $TempInstaller
    $PythonExe = "$PrivatePythonDir\python.exe"
}

# 3. Destination Directory Prompt
$DefaultInstallDir = "$env:LOCALAPPDATA\AIConversationCLI"
Write-Host ""
Write-Host "Where would you like to install AI Conversation CLI?" -ForegroundColor Cyan
Write-Host "Default: $DefaultInstallDir" -ForegroundColor Gray
$UserDir = Read-Host "Enter path (leave empty for default)"
$InstallDir = if ([string]::IsNullOrWhiteSpace($UserDir)) { $DefaultInstallDir } else { $UserDir.Trim() }

Write-Host "Selected installation directory: $InstallDir" -ForegroundColor Gray
if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

# 4. Virtual Environment Creation
$VenvDir = Join-Path $InstallDir "venv"
Write-Host "Creating isolated environment at $VenvDir..." -ForegroundColor Cyan
& $PythonExe -m venv $VenvDir

$VenvPip = Join-Path $VenvDir "Scripts\pip.exe"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$VenvCli = Join-Path $VenvDir "Scripts\ai-conversation.exe"

# 5. Install Dependencies and CLI
Write-Host "Installing AI Conversation CLI and dependencies..." -ForegroundColor Cyan
$RepoRoot = (Get-Item $PSScriptRoot).Parent.FullName
& $VenvPip install --upgrade pip | Out-Null
& $VenvPip install $RepoRoot

# 6. PATH Registration
$VenvScriptsDir = Join-Path $VenvDir "Scripts"
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$VenvScriptsDir*") {
    Write-Host "Adding $VenvScriptsDir to User PATH..." -ForegroundColor Cyan
    $NewPath = if ([string]::IsNullOrEmpty($UserPath)) { $VenvScriptsDir } else { "$UserPath;$VenvScriptsDir" }
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
    Write-Host "✓ PATH updated." -ForegroundColor Green
} else {
    Write-Host "✓ CLI directory is already on PATH." -ForegroundColor Gray
}

# 7. Smoke Test Verification
Write-Host ""
Write-Host "Running smoke test..." -ForegroundColor Cyan
if (Test-Path $VenvCli) {
    & $VenvCli --version
    & $VenvCli doctor
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "    AI Conversation CLI installed successfully!   " -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "You can now run 'ai-conversation' from any new PowerShell or CMD window." -ForegroundColor White
} else {
    Write-Host "Warning: Executable not found at $VenvCli" -ForegroundColor Yellow
}
