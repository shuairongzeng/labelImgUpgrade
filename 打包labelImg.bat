@echo off
echo ��ʼ���labelImg...
echo.

echo ����1: ʹ��spec�ļ�
pyinstaller labelImg.spec
if %errorlevel% neq 0 (
    echo ����1ʧ�ܣ����Է���2...
    echo.
    
    echo ����2: ʹ�������в���
    pyinstaller --hidden-import=pyqt5 --hidden-import=lxml --add-data "data;data" --add-data "resources;resources" -F -n "labelImg" -c labelImg.py -p ./libs -p ./
    if %errorlevel% neq 0 (
        echo ���ʧ�ܣ�
        pause
        exit /b 1
    )
)

echo.
echo �����ɣ�
echo ��ִ���ļ�λ��: dist\labelImg.exe
echo.
echo ��������...
cd dist
labelImg.exe
cd ..

pause
