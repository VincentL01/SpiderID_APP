@echo off

set repo=https://github.com/WongKinYiu/yolov7.git
set target_dir=%cd%\bin\yolov7

if not exist "%target_dir%" (
  echo Cloning YOLOv7 repository...
  git clone %repo% %target_dir%
) else (
  echo YOLOv7 repository already exists.
)

pip install -r requirements.txt

echo Done.