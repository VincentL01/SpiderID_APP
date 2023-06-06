@echo off
set "venv_name=test"
if exist "%USERPROFILE%\anaconda3" (
  set "conda_path=%USERPROFILE%\anaconda3"
) else (
  set "conda_path=%USERPROFILE%\miniconda3"
)
echo Activating virtual environment...
echo Locating virtual environment in %conda_path%\envs\%venv_name%
call %conda_path%\Scripts\activate.bat %conda_path%\envs\%venv_name%
echo Run Program
python main.py
pause