param(
  [string]$RepoRoot = (Get-Location).Path,
  [string]$Branch = 'carson/r9-durable-runner',
  [string]$CheckpointRoot = "$env:USERPROFILE\XAUUSD-Tick-Research\R9_Durable_Checkpoints",
  [string]$PythonExe = ''
)
$ErrorActionPreference='Stop'
$Daemon=Join-Path $RepoRoot 'research\R9_Rebuild\r9_durable_daemon.py'
$Watchdog=Join-Path $RepoRoot 'research\R9_Rebuild\r9_daemon_watchdog.ps1'
if (!(Test-Path $Daemon)) { throw "Missing daemon: $Daemon" }
if (!(Test-Path $Watchdog)) { throw "Missing watchdog: $Watchdog" }
if ([string]::IsNullOrWhiteSpace($PythonExe)) { $PythonExe=(Get-Command python -ErrorAction Stop).Source }
New-Item -ItemType Directory -Force -Path $CheckpointRoot | Out-Null

$DaemonArgs="`"$Daemon`" --repo-root `"$RepoRoot`" --branch `"$Branch`" --checkpoint-root `"$CheckpointRoot`""
$DaemonAction=New-ScheduledTaskAction -Execute $PythonExe -Argument $DaemonArgs -WorkingDirectory $RepoRoot
$DaemonTrigger=New-ScheduledTaskTrigger -AtLogOn
$DaemonSettings=New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 3650) -MultipleInstances IgnoreNew
$Principal=New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName 'R9-Durable-Research' -Action $DaemonAction -Trigger $DaemonTrigger -Settings $DaemonSettings -Principal $Principal -Force | Out-Null

$WdArgs="-NoProfile -ExecutionPolicy Bypass -File `"$Watchdog`" -CheckpointRoot `"$CheckpointRoot`""
$WdAction=New-ScheduledTaskAction -Execute "powershell.exe" -Argument $WdArgs -WorkingDirectory $RepoRoot
$WdTrigger=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration (New-TimeSpan -Days 3650)
$WdSettings=New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName 'R9-Durable-Watchdog' -Action $WdAction -Trigger $WdTrigger -Settings $WdSettings -Principal $Principal -Force | Out-Null

Start-ScheduledTask -TaskName 'R9-Durable-Research'
Start-ScheduledTask -TaskName 'R9-Durable-Watchdog'
Write-Host "Installed R9 durable daemon + watchdog"
Write-Host "Python: $PythonExe"
Write-Host "Repo: $RepoRoot"
Write-Host "Checkpoints: $CheckpointRoot"
