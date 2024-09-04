@echo off

REM Brisanje config.h datoteke
del "path\to\your\project\config.h"

REM Kopiranje config_org.h datoteke i preimenovanje u config.h
copy "path\to\your\project\config_org.h" "path\to\your\project\config.h"

exit



