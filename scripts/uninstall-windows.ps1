# ChatPrint CLI - Windows Uninstaller
# Cleans up PATH environment variables and removes installed files.

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "          ChatPrint CLI Uninstaller               " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Identify installed location
$InstallDir = $null
$MarkerPath = Join-Path $env:USERPROFILE ".chatprint\install_path.txt"

# Method A: Check install record marker
if (Test-Path $MarkerPath) {
    try {
        $Recorded = (Get-Content $MarkerPath -Raw -ErrorAction SilentlyContinue).Trim()
        if ($Recorded -and (Test-Path $Recorded)) {
            $InstallDir = $Recorded
        }
    } catch {}
}

# Method B: Search User PATH
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if (-not $InstallDir -and -not [string]::IsNullOrEmpty($UserPath)) {
    $MatchedPaths = $UserPath -split ';' | Where-Object { 
        $_ -and ($_ -like "*ChatPrintCLI*" -or $_ -like "*chatprint*") 
    }
    if ($MatchedPaths.Count -gt 0) {
        $FirstScriptPath = $MatchedPaths[0].TrimEnd('\')
        if ($FirstScriptPath -like "*\venv\Scripts") {
            $Candidate = Split-Path (Split-Path $FirstScriptPath -Parent) -Parent
        } elseif ($FirstScriptPath -like "*\Scripts") {
            $Candidate = Split-Path $FirstScriptPath -Parent
        } else {
            $Candidate = $FirstScriptPath
        }
        if (Test-Path $Candidate) {
            $InstallDir = $Candidate
        }
    }
}

# Method C: Scan fixed drive roots (e.g. E:\ChatPrintCLI, D:\ChatPrintCLI, C:\ChatPrintCLI)
if (-not $InstallDir) {
    try {
        $Drives = Get-PSDrive -PSProvider FileSystem | Select-Object -ExpandProperty Root
        foreach ($Root in $Drives) {
            $Candidate = Join-Path $Root "ChatPrintCLI"
            if (Test-Path $Candidate) {
                $InstallDir = $Candidate
                break
            }
        }
    } catch {}
}

# Method D: Fallback to default local AppData
$DefaultDir = "$env:LOCALAPPDATA\ChatPrintCLI"
if (-not $InstallDir -and (Test-Path $DefaultDir)) {
    $InstallDir = $DefaultDir
}

# Prompt user for confirmation / custom path
if ($InstallDir) {
    Write-Host "Detected installation at: $InstallDir" -ForegroundColor Yellow
    $UserCustom = Read-Host "Press Enter to uninstall this folder, or enter path if different"
    if (-not [string]::IsNullOrWhiteSpace($UserCustom)) {
        $InstallDir = $UserCustom.Trim()
    }
} else {
    Write-Host "Could not automatically locate the ChatPrint CLI installation folder." -ForegroundColor Yellow
    $UserCustom = Read-Host "Enter the installation folder to remove (or leave empty to cancel)"
    if ([string]::IsNullOrWhiteSpace($UserCustom)) {
        Write-Host "Uninstallation canceled." -ForegroundColor Gray
        exit 0
    }
    $InstallDir = $UserCustom.Trim()
}

$Confirm = Read-Host "Are you sure you want to uninstall ChatPrint CLI from '$InstallDir'? [y/N]"
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
    Write-Host "[OK] Cleaned ChatPrint CLI from User PATH." -ForegroundColor Green
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

# 4. Remove install marker
if (Test-Path (Join-Path $env:USERPROFILE ".chatprint")) {
    try {
        Remove-Item -Path (Join-Path $env:USERPROFILE ".chatprint") -Recurse -Force -ErrorAction SilentlyContinue
    } catch {}
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "   ChatPrint CLI uninstalled successfully!        " -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "You can close this window." -ForegroundColor White
