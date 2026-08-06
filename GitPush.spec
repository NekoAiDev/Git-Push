# -*- mode: python ; coding: utf-8 -*-
import glob
import os
import sys

# Python 3.13 的 python313.dll 依赖 vcruntime140_1.dll，PyInstaller 不会自动带上，
# 在干净 Windows 环境（PATH 不含 Python）双击启动会报 "LoadLibrary: 找不到指定的模块"。
# 这里显式把 vcruntime140_1.dll 也打包进单文件根目录，确保离线/未装 Python 的机器也能启动。
_vcr140_1_paths = glob.glob(os.path.join(os.path.dirname(sys.executable), 'vcruntime140_1.dll'))
if not _vcr140_1_paths:
    _vcr140_1_paths = glob.glob(r'C:\Windows\System32\vcruntime140_1.dll')
_vcr_binaries = [(p, '.') for p in _vcr140_1_paths]

a = Analysis(
    ['git_push_tool.py'],
    pathex=[],
    binaries=_vcr_binaries,
    datas=[('appicon.ico', '.')],
    hiddenimports=[],
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
    name='GitPush',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['appicon.ico'],
)
