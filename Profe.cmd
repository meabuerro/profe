@echo off
REM Profe - arranca la app local y abre el navegador predeterminado.
setlocal
cd /d "%~dp0"

where py >/dev/null 2>/dev/null
if %ERRORLEVEL%==0 (
  py -3 scripts\profe_server.py %*
  exit /b %ERRORLEVEL%
)

where python >/dev/null 2>/dev/null
if %ERRORLEVEL%==0 (
  python scripts\profe_server.py %*
  exit /b %ERRORLEVEL%
)

echo Profe necesita Python 3. Instalalo desde https://www.python.org/downloads/ y vuelve a intentarlo.
exit /b 1
