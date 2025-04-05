@echo off
cd /d C:\Proyectos\crowdfunding
call env\Scripts\activate
python manage.py cerrar_campanas
pause
