# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs

datas = []
binaries = []
datas += collect_data_files('kivy')
datas += collect_data_files('kivy_deps.sdl2')
datas += collect_data_files('kivy_deps.glew')
datas += collect_data_files('kivy_deps.angle')
datas += collect_data_files('kivymd')
binaries += collect_dynamic_libs('kivy')
binaries += collect_dynamic_libs('kivy_deps.sdl2')
binaries += collect_dynamic_libs('kivy_deps.glew')
binaries += collect_dynamic_libs('kivy_deps.angle')
binaries += collect_dynamic_libs('kivymd')


a = Analysis(
    ['Dooka.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
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
    [],
    exclude_binaries=True,
    name='DOOKA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\image\\DOOKA_logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DOOKA',
)
