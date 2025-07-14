@echo off
echo 开始打包labelImg...
echo.

echo 方法1: 使用spec文件
pyinstaller labelImg.spec
if %errorlevel% neq 0 (
    echo 方法1失败，尝试方法2...
    echo.
    
    echo 方法2: 使用命令行参数
    pyinstaller --hidden-import=pyqt5 --hidden-import=lxml --add-data "data;data" --add-data "resources;resources" -F -n "labelImg" -c labelImg.py -p ./libs -p ./
    if %errorlevel% neq 0 (
        echo 打包失败！
        pause
        exit /b 1
    )
)

echo.
echo 打包完成！
echo 可执行文件位置: dist\labelImg.exe
echo.
echo 测试运行...
cd dist
labelImg.exe
cd ..

pause
