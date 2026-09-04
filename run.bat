@echo off
set "VENV_DIR=.venv"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Criando ambiente virtual Python...
    python -m venv %VENV_DIR%
)

echo Ativando ambiente virtual...
call %VENV_DIR%\Scripts\activate.bat

echo Instalando/Atualizando dependencias...
pip install -r requirements.txt

echo Iniciando o Modbus Scanner localmente...
start http://127.0.0.1:8000
python -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
