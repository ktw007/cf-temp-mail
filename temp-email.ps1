# Cloudflare Email Routing CLI - PowerShell Wrapper

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check .env file
$EnvFile = Join-Path $ScriptDir ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Host "Error: .env file not found" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure it:"
    Write-Host "  copy .env.example .env"
    exit 1
}

# Load environment variables from .env
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.+?)\s*$') {
        $name = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($name, $value, 'Process')
    }
}

# Check Python
try {
    $null = python --version 2>&1
} catch {
    Write-Host "Error: Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.6 or higher"
    exit 1
}

# Execute Python script
$PythonScript = Join-Path $ScriptDir "temp_email.py"
python $PythonScript $args
