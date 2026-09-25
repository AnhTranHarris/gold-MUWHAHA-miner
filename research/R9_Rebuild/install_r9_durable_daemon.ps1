param(
  [string]$RepoRoot = (Get-Location).Path,
  [string]$Branch = 'carson/r9-durable-runner',
  [string]$CheckpointRoot = "$env:USERPROFILE\XAUUSD-Tick-Research\R9_Durable_Checkpoints",
  [string]$PythonExe = 'python'
)
$ErrorActionPreference='Stop'
$Daemon = Join-Path $RepoRoot 'research\R9_Rebuild\r9_durable_daemon.py'
if (!(Test-Path $Daemon)) { throw "Missing daemon: $Daemon" }
New-Item -ItemType Directory -Force -Path $CheckpointRoot | Out-Null
$Args = "`"$Daemon`" --repo-root `"$RepoRoot`" --branch `"$Branch`" --checkpoint-root `"$CheckpointRoot`""
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $Args -WorkingDirectory $RepoRoot
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 3650) -MultipleInstances IgnoreNew
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName 'R9-Durable-Research' -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force | Out-Null
Start-ScheduledTask -TaskName 'R9-Durable-Research'
Write-Host "Installed and started R9-Durable-Research"
Write-Host "Repo: $RepoRoot"
Write-Host "Branch: $Branch"
Write-Host "Checkpoints: $CheckpointRoot"
