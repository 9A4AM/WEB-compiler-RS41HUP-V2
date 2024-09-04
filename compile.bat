@echo off

REM Pokretanje exe datoteke
start "" "putanja_do_vase_exe_datoteke.exe"

REM Pauza od 5 sekundi
timeout /t 5 /nobreak >nul

REM Slanje F7 karaktera pomoću PowerShell-a
powershell -command "$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys('{F7}')"

REM Pauza od 5 sekundi
timeout /t 5 /nobreak >nul

REM Zatvaranje exe aplikacije
taskkill /f /im ime_vase_exe_datoteke.exe

exit
