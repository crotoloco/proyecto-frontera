$ErrorActionPreference = 'Stop'

$repo = 'C:\Users\USUARIO\Downloads\frontera_living_python'
$python = 'C:\Program Files\Python311\python.exe'
$logDir = Join-Path $repo 'logs'

if (-not (Test-Path $python)) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $python = $pythonCmd.Source
    }
}

if (-not $python -or -not (Test-Path $python)) {
    throw "No se encontró Python. Instala Python 3.11 y asegúrate que esté disponible en PATH."
}

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$logPath = Join-Path $logDir "automation_$timestamp.log"

Write-Host "Ejecutando automatización cada 15 minutos..."
Write-Host "Repositorio: $repo"
Write-Host "Python: $python"

while ($true) {
    $runTs = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $msg = "[$runTs] Ejecutando AUTOMATIZAR_TODO.py"
    Write-Host $msg
    Add-Content -Path $logPath -Value $msg

    try {
        & $python (Join-Path $repo 'scripts\AUTOMATIZAR_TODO.py') *>> $logPath
        $ok = "[$runTs] Ejecución exitosa"
        Write-Host $ok
        Add-Content -Path $logPath -Value $ok
    }
    catch {
        $err = "[$runTs] ERROR: $($_.Exception.Message)"
        Write-Host $err -ForegroundColor Red
        Add-Content -Path $logPath -Value $err
    }

    Start-Sleep -Seconds 900
}
