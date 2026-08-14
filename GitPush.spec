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
# Python 3.13 的 python313.dll 同时依赖 vcruntime140.dll（不带 _1），也显式带上，双保险
_vcr140_paths = glob.glob(os.path.join(os.path.dirname(sys.executable), 'vcruntime140.dll'))
if not _vcr140_paths:
    _vcr140_paths = glob.glob(r'C:\Windows\System32\vcruntime140.dll')
_vcr_binaries = [(p, '.') for p in (_vcr140_1_paths + _vcr140_paths)]

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
    # 解压目录改到用户可写的 LocalAppData，避免 %TEMP% 被杀毒/组策略拦截导致 python313.dll 加载失败。
    # 注意：必须用 os.environ 在【构建期】展开成真实绝对路径，不能写 "%LOCALAPPDATA%" 字面量（PyInstaller 不展开，
    # 运行时拿到无效路径会回退到默认的 Temp\_MEI*，导致 v1.4.2 仍报 Failed to load Python DLL）。
    runtime_tmpdir=os.path.join(os.environ.get('LOCALAPPDATA', os.environ.get('TEMP', '.')), 'GitPush', 'rt'),
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['appicon.ico'],
)
