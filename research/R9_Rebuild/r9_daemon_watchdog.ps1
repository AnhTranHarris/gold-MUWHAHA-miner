param(
  [string]$CheckpointRoot = "$env:USERPROFILE\XAUUSD-Tick-Research\R9_Durable_Checkpoints",
  [string]$TaskName = "R9-Durable-Research",
  [int]$StaleSeconds = 180
)
$ErrorActionPreference="SilentlyContinue"
$Health=Join-Path $CheckpointRoot "daemon_health.json"
$Restart=$false
if (!(Test-Path $Health)) { $Restart=$true }
else {
  try {
    $j=Get-Content $Health -Raw | ConvertFrom-Json
    $last=[DateTimeOffset]::Parse($j.heartbeat_utc)
    if ((([DateTimeOffset]::UtcNow-$last).TotalSeconds) -gt $StaleSeconds) { $Restart=$true }
  } catch { $Restart=$true }
}
$task=Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue\n# A newly-started running daemon may not yet have emitted its periodic heartbeat.\n# Do not kill a running task solely because the prior health file is stale; the daemon now writes an immediate startup heartbeat.\nif ($null -ne $task -and $task.State -eq "Running" -and $Restart) {\n  try {\n    $info=Get-ScheduledTaskInfo -TaskName $TaskName\n    if ($info.LastRunTime -and ((Get-Date)-$info.LastRunTime).TotalSeconds -lt 90) { $Restart=$false }\n  } catch {}\n}
if ($null -eq $task) { exit 2 }
if ($task.State -eq "Disabled") { Enable-ScheduledTask -TaskName $TaskName | Out-Null; $Restart=$true }
if ($task.State -ne "Running") { $Restart=$true }
if ($Restart) {
  Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
  Start-ScheduledTask -TaskName $TaskName
}
