@echo off
echo ====================================
echo  Sync Notion -> Dashboard
echo ====================================
echo.
echo Sincronizando datos desde archivos locales...
python sync_notion.py
echo.
echo Generando dashboard...
echo (dashboard.html ya existe - usa los datos de data.json)
echo.
echo ====================================
echo  Listo! Abre dashboard.html
echo ====================================
pause