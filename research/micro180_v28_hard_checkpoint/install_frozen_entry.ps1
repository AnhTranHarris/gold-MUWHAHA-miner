#Requires -Version 5.1
<#[
MICRO180 V28 HARD CHECKPOINT - safe entry-only installation, no trade execution.

Usage: .\install_frozen_entry.ps1 -Mql5Directory 'C:\...\MQL5' -CommonFilesDirectory 'C:\...\Terminal\Common\Files'
Optional: -MetaEditorPath 'C:\...\metaeditor64.exe' -Compile
Does NOT overwrite different existing EA/weight files.
#>
param(
  [Parameter(Mandatory=$true)][string]$Mql5Directory,
  [Parameter(Mandatory=$true)][string]$CommonFilesDirectory,
  [string]$MetaEditorPath,
  [switch]$Compile
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$ea='GoldMuwahahaMiner_MICRO180_V28_FrozenEntry.mq5'
$weights='MICRO180_Jan_through_07_merged_weights.tsv'
$sha='92719AE1EDD78C91E63F151DA7D2F3607C7D5F42119B07613B8B20A7CCE3997B'
$actual=(Get-FileHash -Algorithm SHA256 (Join-Path $root $weights)).Hash
if($actual -ne $sha){ throw "Frozen model HASH MISMATCH: $actual" }
$eaDir=Join-Path $Mql5Directory 'Experts'
New-Item -ItemType Directory -Force -Path $eaDir,$CommonFilesDirectory | Out-Null
function Install-Exact($source,$dest){
 if(Test-Path -LiteralPath $dest){
  $h1=(Get-FileHash -Algorithm SHA256 $source).Hash
  $h2=(Get-FileHash -Algorithm SHA256 $dest).Hash
  if($h1 -ne $h2){throw "REFUSED OVERWRITE: $dest (different bytes)"}
  Write-Host "UNCHANGED existing: $dest"
 } else {Copy-Item -LiteralPath $source -Destination $dest -ErrorAction Stop; Write-Host "Installed $dest"}
}
$eaDest=Join-Path $eaDir $ea
Install-Exact (Join-Path $root $ea) $eaDest
Install-Exact (Join-Path $root $weights) (Join-Path $CommonFilesDirectory $weights)
if($Compile){
 if([string]::IsNullOrWhiteSpace($MetaEditorPath) -or -not(Test-Path -LiteralPath $MetaEditorPath)){
  throw 'Supply an existing -MetaEditorPath for -Compile.'
 }
 $log=Join-Path $root 'metaeditor_compile.log'
 $args=@('/compile:'+('"'+$eaDest+'"'), '/log:'+('"'+$log+'"'))
 & $MetaEditorPath @args
 Write-Host "MetaEditor completed. Inspect compiler diagnostics: $log"
}
Write-Host 'Entry-only shadow checkpoint installed. NO orders are placed.'