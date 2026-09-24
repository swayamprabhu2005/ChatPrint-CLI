# ChatPrint CLI - Windows Uninstaller
# Cleans up PATH environment variables and removes installed files.

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "          ChatPrint CLI Uninstaller               " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Identify installed location from User PATH
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$MatchedPaths = @()
if (-not [string]::IsNullOrEmpty($UserPath)) {
    $MatchedPaths = $UserPath -split ';' | Where-Object { 
        $_ -and ($_ -like "*ChatPrintCLI*" -or $_ -like "*chatprint*") 
    }
}

$InstallDir = $null
if ($MatchedPaths.Count -gt 0) {
    # e.g. E:\ChatPrintCLI\venv\Scripts -> E:\ChatPrintCLI
    $FirstScriptPath = $MatchedPaths[0].TrimEnd('\')
    if ($FirstScriptPath -like "*\venv\Scripts") {
        $InstallDir = Split-Path (Split-Path $FirstScriptPath -Parent) -Parent
    } elseif ($FirstScriptPath -like "*\Scripts") {
        $InstallDir = Split-Path $FirstScriptPath -Parent
    } else {
        $InstallDir = $FirstScriptPath
    }
}

$DefaultDir = "$env:LOCALAPPDATA\ChatPrintCLI"
if (-not $InstallDir -or -not (Test-Path $InstallDir)) {
    if (Test-Path $DefaultDir) {
        $InstallDir = $DefaultDir
    }
}

if ($InstallDir) {
    Write-Host "Detected installation at: $InstallDir" -ForegroundColor Yellow
} else {
    Write-Host "Could not automatically locate the ChatPrint CLI installation directory." -ForegroundColor Yellow
}

$Confirm = Read-Host "Are you sure you want to uninstall ChatPrint CLI? [y/N]"
if ($Confirm -notmatch "^[yY]$") {
    Write-Host "Uninstallation canceled." -ForegroundColor Gray
    exit 0
}

# 2. Clean up User PATH
if (-not [string]::IsNullOrEmpty($UserPath)) {
    $NewEntries = $UserPath -split ';' | Where-Object { 
        $_ -and ($_ -notlike "*ChatPrintCLI*" -and $_ -notlike "*chatprint*") 
    }
    $NewPath = $NewEntries -join ';'
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
    Write-Host "[OK] Removed ChatPrint CLI from User PATH." -ForegroundColor Green
}

# 3. Remove Installed Directory
if ($InstallDir -and (Test-Path $InstallDir)) {
    try {
        Write-Host "Removing installation files at $InstallDir..." -ForegroundColor Cyan
        Remove-Item -Path $InstallDir -Recurse -Force -ErrorAction Stop
        Write-Host "[OK] Installation files removed." -ForegroundColor Green
    } catch {
        Write-Host "Note: Some files could not be removed automatically: $_" -ForegroundColor Yellow
        Write-Host "You can manually delete the folder: $InstallDir" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "   ChatPrint CLI uninstalled successfully!        " -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "You can close this window." -ForegroundColor White
