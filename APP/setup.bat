@echo off
set miniconda_url="https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
set miniconda_installer="%~dp0Miniconda3-latest-Windows-x86_64.exe"
set python_version="3.9.13"
set venv_name="spiderid_venv"

set spiderid_dir=C:\SpiderID

echo The SpiderID_APP application would be installed by default at %APP_INSTALL_PATH%
set /p change_path=Do you want to change? (Y/N)

if /i "%change_path%"=="Y" (
    set /p spiderid_dir=Enter the new installation path:
)

echo The SpiderID_APP application will be installed at %spiderid_dir%

if not exist "%UserProfile%\miniconda3" (
  if not exist "%UserProfile%\anaconda3" (
    echo Downloading Miniconda...
    powershell.exe -Command "(New-Object System.Net.WebClient).DownloadFile('%miniconda_url%', '%miniconda_installer%')"

    echo Installing Miniconda...
    start /wait "" "%miniconda_installer%" /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=%UserProfile%\miniconda3
  )
)

if exist "%UserProfile%\anaconda3" (
  set "conda_path=%UserProfile%\anaconda3\Scripts"
) else (
  set "conda_path=%UserProfile%\miniconda3\Scripts"
)

REM Task 1
set "venv_exists=0"
for /f "tokens=*" %%a in ('%conda_path%\conda env list') do (
  for /f "tokens=1" %%b in ("%%a") do (
    if /i "%%b"=="%venv_name%" (
      set "venv_exists=1"
    )
  )
)

if %venv_exists%==1 (
  echo Virtual environment %venv_name% already exists. Checking Python version...
  for /f "tokens=*" %%a in ('%conda_path%\conda list --revisions -n %venv_name%') do (
    for /f "tokens=1-3" %%b in ("%%a") do (
      if /i "%%b"=="python" (
        if not "%%c"=="%python_version%" (
          echo Python version mismatch. Creating alternate environment...
          set "venv_name=spiderid_venv_alt"
          call %conda_path%\conda create -n %venv_name% python=%python_version% -y
        )
      )
    )
  )
) else (
  echo Creating virtual environment with Python %python_version%...
  call %conda_path%\conda create -n %venv_name% python=%python_version% -y
)

echo Activating virtual environment...
call %conda_path%\activate.bat %conda_path%\..\envs\%venv_name%

REM Check if Git is installed
where git >nul 2>nul
if errorlevel 1 (
  echo Downloading and installing Git...
  call conda install -c anaconda git -y
) else (
  echo Git is already installed. Skipping installation.
)

echo Virtual environment setup complete. You can now use Git and other tools within this environment.

REM Task 2
if exist "%spiderid_dir%" (
  set /p "user_input=The folder C:\SpiderID already exists. Do you want to overwrite it? (Y/N): "
  if /i "%user_input%"=="Y" (
    echo Removing existing SpiderID folder...
    rmdir /s /q "%spiderid_dir%"
  ) else (
    goto CloneYOLOv7
  )
)

echo Make folder for spiderid at %spiderid_dir%
mkdir "%spiderid_dir%"

echo Clone SpiderID repository from https://github.com/ThangLC304/SpiderID_APP to spiderid_dir
set "spider_repo=https://github.com/ThangLC304/SpiderID_APP"
git clone %spider_repo% "%spiderid_dir%"

:CloneYOLOv7
echo Change directory to %spiderid_dir%
cd "%spiderid_dir%"

set "yolo_repo=https://github.com/WongKinYiu/yolov7.git"
set "target_dir=%spiderid_dir%\bin\yolov7"

REM Task 3
if exist "%target_dir%" (
  set /p "user_input=The folder %spiderid_dir%\bin\yolov7 already exists. Do you want to overwrite it? (Y/N): "
  if /i "%user_input%"=="Y" (
    echo Removing existing YOLOv7 folder...
    rmdir /s /q "%target_dir%"
  ) else (
    goto InstallYOLOv7
  )
)

echo Cloning YOLOv7 repository...
git clone %yolo_repo% "%target_dir%"

:InstallYOLOv7
echo Installing YOLOv7 requirements...
pip install -r requirements.txt"

echo Copying detect.py to %target_dir% folder...
copy detect.py "%target_dir%" /y

REM Task 4
echo Creating run.bat file...
if exist run.bat (
  del run.bat
)

(
Echo @echo off
Echo set "venv_name=%venv_name%"
Echo if exist "%%USERPROFILE%%\anaconda3" ^(
Echo   set "conda_path=%%USERPROFILE%%\anaconda3"
Echo ^) else ^(
Echo   set "conda_path=%%USERPROFILE%%\miniconda3"
Echo ^)
Echo echo Activating virtual environment...
Echo echo Locating virtual environment in %%conda_path%%\envs\%%venv_name%%
Echo call %%conda_path%%\Scripts\activate.bat %%conda_path%%\envs\%%venv_name%%
Echo echo Run Program
Echo python main.py
Echo pause
) > run.bat

echo run.bat created.

echo =============================
echo    INSTALLATION COMPLETED
echo =============================
echo .
echo PLEASE RUN THE SpiderID_APP from run.bat file located in C:\SpiderID folder.
echo .
pause
