@echo off
setlocal EnableExtensions

set "ROOT=%~dp0.."
set "EA=%ROOT%\Experts\GoldMuwahahaMiner_R9_STMR_XMonth_001.mq5"
set "LOG=%ROOT%\Experts\GoldMuwahahaMiner_R9_STMR_XMonth_001.log"

if not defined METAEDITOR_EXE (
  if exist "C:\Program Files\Coinexx MetaTrader 5\metaeditor64.exe" set "METAEDITOR_EXE=C:\Program Files\Coinexx MetaTrader 5\metaeditor64.exe"
)
if not defined METAEDITOR_EXE (
  if exist "C:\Program Files\MetaTrader 5\metaeditor64.exe" set "METAEDITOR_EXE=C:\Program Files\MetaTrader 5\metaeditor64.exe"
)

if not defined METAEDITOR_EXE (
  echo ERROR: MetaEditor was not found.
  echo Set METAEDITOR_EXE to your metaeditor64.exe path, then rerun.
  exit /b 2
)
if not exist "%METAEDITOR_EXE%" (
  echo ERROR: METAEDITOR_EXE does not exist: %METAEDITOR_EXE%
  exit /b 2
)
if not exist "%EA%" (
  echo ERROR: EA not found: %EA%
  exit /b 2
)

if exist "%LOG%" del /q "%LOG%"

echo Compiling:
echo   %EA%
echo With:
echo   %METAEDITOR_EXE%
"%METAEDITOR_EXE%" /compile:"%EA%" /log

if not exist "%LOG%" (
  echo ERROR: MetaEditor did not create the expected log:
  echo   %LOG%
  exit /b 3
)

type "%LOG%"
findstr /C:"0 errors, 0 warnings" "%LOG%" >nul
if errorlevel 1 (
  echo.
  echo BUILD GATE FAILED. Do not run Strategy Tester until MetaEditor reports 0 errors, 0 warnings.
  exit /b 1
)

echo.
echo BUILD GATE PASSED: 0 errors, 0 warnings.
exit /b 0
