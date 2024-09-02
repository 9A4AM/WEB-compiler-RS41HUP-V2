@echo off

REM Pokretanje exe datoteke
start "" "C:\CooCox\CoIDE\CoIDE.exe"

REM Pauza od 5 sekundi
timeout /t 10 /nobreak >nul

REM Slanje F7 karaktera pomoću PowerShell-a
powershell -command "$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys('{F7}')"

REM Pauza od 5 sekundi
timeout /t 10 /nobreak >nul

REM Zatvaranje exe aplikacije
taskkill /f /im CoIDE.exe

REM Pauza od 5 sekundi
timeout /t 5 /nobreak >nul

REM Brisanje config.h datoteke
del "C:\Users\9A4AM\Desktop\RS41HUP_V2-9A4AM\config.h"

REM Kopiranje config_org.h datoteke i preimenovanje u config.h
copy "C:\Users\9A4AM\Desktop\RS41HUP_V2-9A4AM\config_org.h" "C:\Users\9A4AM\Desktop\RS41HUP_V2-9A4AM\config.h"

exit
