# -*- mode: python ; coding: utf-8 -*-

import os

# 获取当前目录的绝对路径
current_dir = os.getcwd()
data_path = os.path.join(current_dir, 'data')
resources_path = os.path.join(current_dir, 'resources')

a = Analysis(
    ['labelImg.py'],
    pathex=[os.path.join(current_dir, 'libs'), current_dir],
    binaries=[],
    datas=[(data_path, 'data'), (resources_path, 'resources')],
    hiddenimports=['pyqt5', 'lxml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='labelImg',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
