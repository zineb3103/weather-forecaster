param(
    [switch]$Clean,
    [int]$WaitSeconds = 8,
    [switch]$Attach
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$kafkaHome   = 'C:\kafka'
$serverProps = Join-Path $kafkaHome 'config\kraft\server.properties'
$storageBat  = Join-Path $kafkaHome 'bin\windows\kafka-storage.bat'
$serverBat   = Join-Path $kafkaHome 'bin\windows\kafka-server-start.bat'
# Déduire log.dirs depuis server.properties (fallback vers dossier par défaut connu)
$serverPropsContent = Get-Content -Path $serverProps -ErrorAction Stop
$logDirsLine = $serverPropsContent | Where-Object { $_ -match '^log\.dirs\s*=\s*' } | Select-Object -First 1
if ($null -ne $logDirsLine) {
    $logDir = ($logDirsLine -split '=',2)[1].Trim()
} else {
    $logDir = Join-Path $kafkaHome 'kafkakraft-combined-logs'
}
# Normaliser les backslashes
$logDir = $logDir -replace '/', '\\'

if (-not (Test-Path $serverProps)) {
    Write-Error "Kafka KRaft server.properties introuvable: $serverProps"
}
if (-not (Test-Path $storageBat)) {
    Write-Error "Fichier manquant: $storageBat"
}
if (-not (Test-Path $serverBat)) {
    Write-Error "Fichier manquant: $serverBat"
}

if ($Clean) {
    Write-Host "[Kafka] Arrêt des processus Java (si présents)..."
    Get-Process -Name java -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    if (Test-Path $logDir) {
        Write-Host "[Kafka] Nettoyage du répertoire de logs: $logDir"
        Remove-Item -Recurse -Force $logDir
    }
}

# Choisir un cluster.id compatible avec meta.properties si existant
$metaPath = Join-Path $logDir 'meta.properties'
if (Test-Path $metaPath -PathType Leaf) {
    $existing = Select-String -Path $metaPath -Pattern '^cluster\.id=' -SimpleMatch | Select-Object -First 1
    if ($existing) {
        $clusterId = ($existing.Line -split '=',2)[1].Trim()
        Write-Host "[Kafka] cluster.id existant détecté: $clusterId"
    } else {
        Write-Host "[Kafka] Génération d'un cluster.id..."
        $raw = cmd /c ('"{0}" random-uuid' -f $storageBat)
        $clusterId = ($raw -split "\s+")[-1].Trim()
    }
} else {
    Write-Host "[Kafka] Génération d'un cluster.id..."
    $raw = cmd /c ('"{0}" random-uuid' -f $storageBat)
    $clusterId = ($raw -split "\s+")[-1].Trim()
}
if (-not $clusterId) { Write-Error 'Échec génération du cluster.id' }
Write-Host "[Kafka] cluster.id: $clusterId"

Write-Host "[Kafka] Formatage du stockage..."
cmd /c ('"{0}" format -t {1} -c "{2}" --ignore-formatted' -f $storageBat, $clusterId, $serverProps) | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Échec du formatage du stockage (vérifier log.dirs et meta.properties)'
}

if ($Attach) {
    Write-Host "[Kafka] Démarrage du broker en mode attaché (Ctrl+C pour arrêter)..."
    & cmd /c ('"{0}" "{1}"' -f $serverBat, $serverProps)
    exit $LASTEXITCODE
} else {
    Write-Host "[Kafka] Démarrage du broker (fenêtre minimisée)..."
    Start-Process -FilePath $serverBat -ArgumentList $serverProps -WindowStyle Minimized | Out-Null
    Start-Sleep -Seconds $WaitSeconds
    try {
        $r = Test-NetConnection -ComputerName localhost -Port 9092 -WarningAction SilentlyContinue
        if ($r.TcpTestSucceeded) {
            Write-Host '[Kafka] Broker OK sur localhost:9092'
            exit 0
        } else {
            Write-Error 'Broker non joignable sur localhost:9092'
        }
    } catch {
        Write-Error $_
    }
}


