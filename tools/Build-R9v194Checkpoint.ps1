#requires -Version 5.1
<#
.SYNOPSIS
Stage and compile the R9 v1.94 SHADOW checkpoint in a NEW MT5 Experts folder.
.DESCRIPTION
Run on Windows with the owner's Coinexx MetaEditor64 executable.
Does NOT launch MT5, switch AutoTrading on, or attach the EA.
Stages only the MQ5/MQH files. Does not move or duplicate any tick archives.
.EXAMPLE
Run from repository root:
powershell -File tools/Build-R9v194Checkpoint.ps1 -MetaEditorPath "C:\Program Files\Coinexx MetaTrader 5\metaeditor64.exe" -TerminalDataPath "%APPDATA%\MetaQuotes\Terminal\YOUR_HASH"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$MetaEditorPath,
    [Parameter(Mandatory=$true)][string]$TerminalDataPath,
    [switch]$OverwriteOwnCheckpoint
)
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"

$root=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$expertRoot=Join-Path $root "Experts"
$meta=(Resolve-Path -LiteralPath $MetaEditorPath -ErrorAction Stop).Path
$terminal=(Resolve-Path -LiteralPath $TerminalDataPath -ErrorAction Stop).Path
if (-not (Test-Path -LiteralPath (Join-Path $terminal "MQL5\Experts") -PathType Container)) {
    throw "Not an MT5 terminal DATA path: missing MQL5\Experts"
}
if ([IO.Path]::GetFileName($meta) -notmatch '^metaeditor64?\.exe$') {
    throw "Expected real MetaEditor executable, not MT5 terminal or unrelated binary"
}
$stage=Join-Path $terminal "MQL5\Experts\R9_v194_Coinexx_Model155_Checkpoint"
New-Item -ItemType Directory -Path $stage -Force | Out-Null
$files=@(
 "GoldMuwahahaMiner_R9_HybridGate.mq5",
 "GoldMuwahahaR9PortfolioGovernor.mqh",
 "GoldMuwahahaR9M1IndicatorContext.mqh",
 "GoldMuwahahaR9CashGeometry.mqh",
 "GoldMuwahahaR9M60ModelBridge.mqh"
)
foreach($file in $files) {
    $from=Join-Path $expertRoot $file
    $to=Join-Path $stage $file
    if(-not (Test-Path -LiteralPath $from -PathType Leaf)) {
        throw "Missing required checkpoint source: $from"
    }
    if(Test-Path -LiteralPath $to -PathType Leaf) {
        $old=(Get-FileHash -Algorithm SHA256 -LiteralPath $to).Hash
        $new=(Get-FileHash -Algorithm SHA256 -LiteralPath $from).Hash
        if($old -ne $new -and -not $OverwriteOwnCheckpoint) {
            throw "Existing staged $file differs. Review it before using -OverwriteOwnCheckpoint."
        }
    }
    Copy-Item -LiteralPath $from -Destination $to -Force
}
$ea=Join-Path $stage "GoldMuwahahaMiner_R9_HybridGate.mq5"
$ex5=[IO.Path]::ChangeExtension($ea,".ex5")
$log=Join-Path $stage "R9_v194_MetaEditor_compile.log"
if(Test-Path $log){ Remove-Item -LiteralPath $log -Force }
$arguments=@("/compile:" + ('"'+$ea+'"'), "/log:" + ('"'+$log+'"'))
Write-Host "Compiling checkpoint in isolated MT5 folder: $stage"
$proc=Start-Process -FilePath $meta -ArgumentList $arguments -Wait -PassThru
if(-not (Test-Path -LiteralPath $log -PathType Leaf)) {
    throw "MetaEditor did not create compile log, status unknown. Exit code: $($proc.ExitCode)"
}
$txt=Get-Content -LiteralPath $log -Raw
Write-Host $txt
if ($txt -match '([1-9][0-9]*)\s+errors?\b' -or
    $txt -notmatch '\b0\s+errors?\b' -or
    -not (Test-Path -LiteralPath $ex5 -PathType Leaf)) {
    throw "MetaEditor compile NOT VERIFIED as zero errors with EX5. Do not deploy."
}
$sha=(Get-FileHash -LiteralPath $ex5 -Algorithm SHA256).Hash
Write-Host "CHECKPOINT COMPILE PASS" -ForegroundColor Green
Write-Host "EX5: $ex5"
Write-Host "SHA256: $sha"
Write-Host "Model mode defaults to SHADOW; filter locked until explicit owner unlock."
Write-Host "No EA attached or live orders executed by this script."
