@echo off
cd /d c:\PROJECTS\Git\EdgeCloudSim

REM Create output directory
if not exist "out" mkdir out

REM Build classpath from lib directory
setlocal enabledelayedexpansion
set "CLASSPATH="
for %%f in (lib\*.jar) do (
    set "CLASSPATH=!CLASSPATH!%%f;"
)

REM Compile all Java sources
echo Compiling Java sources...
for /r src %%f in (*.java) do (
    set "SOURCES=!SOURCES! %%f"
)

c:\DEV\Java\jdk-25\bin\javac.exe -d out -cp %CLASSPATH% %SOURCES%

if %ERRORLEVEL% equ 0 (
    echo Compilation successful!
) else (
    echo Compilation failed!
    exit /b 1
)
