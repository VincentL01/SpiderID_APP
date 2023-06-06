FROM mcr.microsoft.com/windows/nanoserver:ltsc2022

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Set timezone
# RUN [System.TimeZoneInfo]::Local | Out-Null

# Install necessary dependencies
RUN Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force ; \
    Install-Module -Name PowerShellGet -Force ; \
    Install-Package -Name 'VisualCppBuildTools' -Source 'chocolatey' -Force
# -RequiredVersion '14.0.25420.1'
# Install python
ARG PYTHON_VERSION=3.9.13
ENV PYTHON_VERSION=${PYTHON_VERSION}
RUN Invoke-WebRequest "https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}.exe" -OutFile python-$env:PYTHON_VERSION.exe ; \
    Start-Process python-${PYTHON_VERSION}.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -NoNewWindow -Wait ; \
    Remove-Item python-${PYTHON_VERSION}.exe -Force

# Install and configure VcXsrv
RUN powershell -Command "Invoke-WebRequest -Uri https://sourceforge.net/projects/vcxsrv/files/latest/download -OutFile vcxsrv.exe" && \
    powershell -Command "Start-Process vcxsrv.exe -ArgumentList '/SILENT' -Wait" && \
    powershell -Command "Remove-Item vcxsrv.exe" && \
    powershell -Command "Set-Variable -Name DISPLAY -Value 'host.docker.internal:0.0' -Option Constant -Scope Global"

# Install necessary python packages
WORKDIR /app
RUN mkdir -p bin
RUN mkdir -p bin/yolov7
RUN mkdir -p bin/weights
RUN mkdir -p utils

ARG yolo_url=https://github.com/WongKinYiu/yolov7.git
ARG target_dir=/app/bin/yolov7
ARG yolov7_detect_path=/app/bin/yolov7/detect.py

RUN git clone $yolo_url $target_dir
COPY detect.py bin\yolov7\detect.py

COPY requirements.txt /app
RUN pip install -r ./requirements.txt
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

COPY bin/weights/v7_NG.pt /app/bin/weights
COPY bin/weights/v7_WG.pt /app/bin/weights
COPY bin/genera_list.csv /app/bin
COPY bin/genera_list_NG.csv /app/bin/
COPY bin/genera_list_WG.csv /app/bin/
COPY bin/landing_photo.jpg /app/bin
COPY utils/utils.py /app/utils

# Set display environment variable
ENV DISPLAY=:99

CMD ["python", "main.py"]